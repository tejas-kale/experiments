"""Model deployment logic for HuggingFace models."""

import json
import time
from typing import Dict, Optional, List
from rich.console import Console
from .ssh_client import SSHClient

console = Console()


class ModelDeployer:
    """Deploys and manages HuggingFace models on RunPod instances."""

    def __init__(self, ssh_client: SSHClient):
        """Initialize model deployer.

        Args:
            ssh_client: Connected SSH client
        """
        self.ssh = ssh_client
        self.model_id: Optional[str] = None
        self.is_vision_model: bool = False
        self.use_vllm: bool = False

    def setup_environment(self) -> bool:
        """Setup Python environment and install dependencies.

        Returns:
            True if successful
        """
        console.print("\n[cyan]Setting up environment...[/cyan]")

        commands = [
            # Update pip
            "pip install --upgrade pip",
            # Install base dependencies
            "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
            "pip install transformers accelerate bitsandbytes pillow requests",
        ]

        for cmd in commands:
            console.print(f"[dim]Running: {cmd}[/dim]")
            exit_code, stdout, stderr = self.ssh.execute_command(cmd, timeout=300)

            if exit_code != 0:
                console.print(f"[yellow]Warning during setup: {stderr}[/yellow]")
                # Continue anyway as some errors might be non-critical

        console.print("[green]Environment setup complete[/green]")
        return True

    def install_vllm(self) -> bool:
        """Install vLLM for optimized inference.

        Returns:
            True if successful
        """
        console.print("\n[cyan]Installing vLLM...[/cyan]")

        cmd = "pip install vllm"
        exit_code, stdout, stderr = self.ssh.execute_command(cmd, timeout=300)

        if exit_code == 0:
            console.print("[green]vLLM installed successfully[/green]")
            return True
        else:
            console.print(f"[yellow]vLLM installation failed, will use transformers: {stderr}[/yellow]")
            return False

    def deploy_model(
        self,
        model_id: str,
        is_vision: bool = False,
        use_vllm: bool = True,
        quantize: bool = False,
    ) -> bool:
        """Deploy a HuggingFace model.

        Args:
            model_id: HuggingFace model ID
            is_vision: Whether model is a vision-language model
            use_vllm: Whether to use vLLM
            quantize: Whether to use quantization

        Returns:
            True if successful
        """
        self.model_id = model_id
        self.is_vision_model = is_vision
        self.use_vllm = use_vllm and not is_vision  # vLLM doesn't support all vision models

        console.print(f"\n[cyan]Deploying model: {model_id}[/cyan]")
        console.print(f"  Vision model: {is_vision}")
        console.print(f"  Using vLLM: {self.use_vllm}")
        console.print(f"  Quantization: {quantize}")

        # Setup environment
        if not self.setup_environment():
            return False

        # Install vLLM if needed
        if self.use_vllm:
            if not self.install_vllm():
                self.use_vllm = False

        # Create model loading script
        if self.use_vllm:
            return self._deploy_vllm_model(model_id, quantize)
        else:
            return self._deploy_transformers_model(model_id, is_vision, quantize)

    def _deploy_vllm_model(self, model_id: str, quantize: bool) -> bool:
        """Deploy model using vLLM.

        Args:
            model_id: HuggingFace model ID
            quantize: Whether to use quantization

        Returns:
            True if successful
        """
        console.print("\n[cyan]Deploying with vLLM...[/cyan]")

        # Create vLLM server script
        script = f'''
import json
import sys
from vllm import LLM, SamplingParams

# Load model
print("Loading model {model_id}...", file=sys.stderr)
llm = LLM(
    model="{model_id}",
    {"quantization='awq'" if quantize else ""},
    gpu_memory_utilization=0.90,
    max_model_len=4096,
)
print("Model loaded successfully!", file=sys.stderr)

# Chat loop
while True:
    try:
        line = input()
        if not line:
            continue

        data = json.loads(line)
        prompt = data.get("prompt", "")
        max_tokens = data.get("max_tokens", 512)
        temperature = data.get("temperature", 0.7)

        sampling_params = SamplingParams(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.9,
        )

        outputs = llm.generate([prompt], sampling_params)
        response = outputs[0].outputs[0].text

        print(json.dumps({{"response": response}}))
        sys.stdout.flush()

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))
        sys.stdout.flush()
'''

        # Upload script
        with open("/tmp/vllm_server.py", "w") as f:
            f.write(script)

        if not self.ssh.upload_file("/tmp/vllm_server.py", "/root/model_server.py"):
            return False

        console.print("[green]vLLM deployment complete[/green]")
        return True

    def _deploy_transformers_model(
        self, model_id: str, is_vision: bool, quantize: bool
    ) -> bool:
        """Deploy model using transformers.

        Args:
            model_id: HuggingFace model ID
            is_vision: Whether model is a vision-language model
            quantize: Whether to use quantization

        Returns:
            True if successful
        """
        console.print("\n[cyan]Deploying with transformers...[/cyan]")

        # Create transformers server script
        vision_imports = """
from PIL import Image
import requests
from io import BytesIO
""" if is_vision else ""

        quantization_config = """
from transformers import BitsAndBytesConfig
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
)
""" if quantize else "quantization_config = None"

        script = f'''
import json
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoProcessor
{vision_imports}

# Load model
print("Loading model {model_id}...", file=sys.stderr)
{quantization_config}

tokenizer = AutoTokenizer.from_pretrained("{model_id}")
{"processor = AutoProcessor.from_pretrained('" + model_id + "')" if is_vision else ""}

model = AutoModelForCausalLM.from_pretrained(
    "{model_id}",
    {"quantization_config=quantization_config," if quantize else ""}
    device_map="auto",
    torch_dtype=torch.float16,
)
print("Model loaded successfully!", file=sys.stderr)

# Chat loop
while True:
    try:
        line = input()
        if not line:
            continue

        data = json.loads(line)
        prompt = data.get("prompt", "")
        max_tokens = data.get("max_tokens", 512)
        temperature = data.get("temperature", 0.7)
        image_url = data.get("image_url")

        {"# Handle vision input" if is_vision else ""}
        {"image = None" if is_vision else ""}
        {"if image_url:" if is_vision else ""}
        {"    if image_url.startswith('http'):" if is_vision else ""}
        {"        response = requests.get(image_url)" if is_vision else ""}
        {"        image = Image.open(BytesIO(response.content))" if is_vision else ""}
        {"    else:" if is_vision else ""}
        {"        image = Image.open(image_url)" if is_vision else ""}
        {"" if is_vision else ""}
        {"if image:" if is_vision else ""}
        {"    inputs = processor(text=prompt, images=image, return_tensors='pt').to(model.device)" if is_vision else ""}
        {"else:" if is_vision else ""}
        {"    inputs = tokenizer(prompt, return_tensors='pt').to(model.device)" if is_vision else ""}
        {"inputs = tokenizer(prompt, return_tensors='pt').to(model.device)" if not is_vision else ""}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=0.9,
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the input prompt from response
        if response.startswith(prompt):
            response = response[len(prompt):].strip()

        print(json.dumps({{"response": response}}))
        sys.stdout.flush()

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))
        sys.stdout.flush()
'''

        # Upload script
        with open("/tmp/transformers_server.py", "w") as f:
            f.write(script)

        if not self.ssh.upload_file("/tmp/transformers_server.py", "/root/model_server.py"):
            return False

        console.print("[green]Transformers deployment complete[/green]")
        return True

    def start_model_server(self) -> bool:
        """Start the model server in the background.

        Returns:
            True if successful
        """
        console.print("\n[cyan]Starting model server...[/cyan]")

        # Start server in background with nohup
        cmd = "nohup python /root/model_server.py > /root/model_server.log 2>&1 &"
        exit_code, stdout, stderr = self.ssh.execute_command(cmd)

        if exit_code == 0:
            console.print("[green]Model server started[/green]")
            # Wait for model to load
            console.print("[cyan]Waiting for model to load (this may take a few minutes)...[/cyan]")
            time.sleep(30)  # Give it time to start loading

            # Check if server is running
            exit_code, stdout, stderr = self.ssh.execute_command("pgrep -f model_server.py")
            if exit_code == 0:
                console.print("[green]Model server is running[/green]")
                return True
            else:
                console.print("[red]Model server failed to start[/red]")
                # Show logs
                self.ssh.execute_command("tail -50 /root/model_server.log", stream_output=True)
                return False
        else:
            console.print(f"[red]Failed to start model server: {stderr}[/red]")
            return False

    def send_chat_message(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        image_path: Optional[str] = None,
    ) -> Optional[str]:
        """Send a chat message to the model.

        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            image_path: Path to image file (for vision models)

        Returns:
            Model response or None if error
        """
        try:
            # Prepare request
            request = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            if image_path and self.is_vision_model:
                request["image_url"] = image_path

            # Send request via stdin
            request_json = json.dumps(request)
            cmd = f"echo '{request_json}' | python /root/model_server.py"

            exit_code, stdout, stderr = self.ssh.execute_command(cmd, timeout=120)

            if exit_code == 0 and stdout:
                response_data = json.loads(stdout.strip())
                if "error" in response_data:
                    console.print(f"[red]Model error: {response_data['error']}[/red]")
                    return None
                return response_data.get("response")
            else:
                console.print(f"[red]Error getting response: {stderr}[/red]")
                return None

        except Exception as e:
            console.print(f"[red]Error sending message: {e}[/red]")
            return None
