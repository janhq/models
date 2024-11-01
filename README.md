# Model Conversion Guide
This guide will help you understand how to convert AI models into different formats that our applications can use.

## What We're Doing
We convert LLMs on HuggingFace into special formats (GGUF, TensorRT, ONNX) so they can work with our applications called [Jan](https://github.com/janhq/jan) and [Cortex](https://github.com/janhq/cortex.cpp). Think of this like converting a video file from one format to another so it can play on different devices.

### New Model Conversion

#### Step 1: Create a New Model Template

This step will create a model repository on [Cortexso's Hugging Face account](https://huggingface.co/cortexso) and then generate two files: `model.yml` as the model's configuration file and `metadata.yml`.

1. Visit: https://github.com/janhq/models/actions/workflows/create-model-yml.yml
2. Click `Run workflow` dropdown
3. Fill in the required information:
  - **`model_name`**: Name of the model to create (will be used in repo name and files)
  - **`prompt_template`**: Prompt template for the model (default: `<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n`)
   - **`stop_tokens`**: Stop tokens for the model (comma-separated, e.g., `,</s>`) (default: `<|im_end|>`)
   - **`engine`**: Engine to run the model (default: `llama-cpp`)
4. Click `Run workflow` button to start the conversion

**Common Errors:**
- Wrong Stop Tokens: If the model keeps generating too much text, check the `stop` tokens in `model.yml`
- Engine Errors: Make sure you picked the right engine type in `model.yml`
- Template Issues: Double-check your `prompt_template` if the model gives weird outputs

#### Step 2: Convert Model

1. Visit: https://github.com/janhq/models/actions/workflows/convert-model-all-quant.yml
2. Choose your conversion type:
- For [GGUF](https://huggingface.co/docs/hub/gguf) format: Click `Convert model to gguf with specified quant`
- For [TensorRT](https://github.com/NVIDIA/TensorRT-LLM): Coming soon
- For [ONNX](https://onnx.ai/): Coming soon
3. Click `Run workflow` dropdown
4. Fill in the required information:
- **`source_model_id`**: The source HuggingFace model ID (e.g., meta-llama/Meta-Llama-3.1-8B-Instruct)
- **`**source_model_size`**: The model size (e.g., 8b)
- **`target_model_id`**: The target HuggingFace model ID
- **`quantization_level`**: Quantization level (e.g., 'q4-km') or 'all' for all levels
5. Click `Run workflow` button to start the conversion

#### Step 3: Check If It Worked

1. Watch the conversion process (it looks like a loading bar)
2. If you see any errors ❌:
- Click on the failed step to see what went wrong
- Create a "Bug Report" on GitHub
- Contact Rex or Alex for help

#### Step 4: Final Testing
After the conversion completes:

1. Check Huggingface page to make sure all files are there
2. Test the model in Cortex:

- Make sure it generates text properly
- Check if it stops generating when it should

For instructions on installing and running the model on Cortex, please refer to the [official documentation](https://cortex.so/docs/)

#### Step 5: Create README For New Model

1. Navigate to the newly created model repository on [Cortexso's Hugging Face account](https://huggingface.co/cortexso)
2. Open the repository and select "Create Model Card"
3. Use the template below for your model card, replacing the example content with your model's information:

```yml
---
license: your_model_license
---

## Overview

[Provide a brief description of your model, including its key features, use cases, and performance characteristics]

## Variants

| No | Variant | Cortex CLI command |
| --- | --- | --- |
| 1 | [variant_name](variant_url) | `cortex run model_name:variant` |
| 2 | [main/default](main_url) | `cortex run model_name` |

## Use with Jan (UI)

1. Install **Jan** from the [Quickstart Guide](https://jan.ai/docs/quickstart)
2. In Jan model Hub, enter:
    ```
    cortexso/your_model_name
    ```

## Use with Cortex (CLI)

1. Install **Cortex** using the [Quickstart Guide](https://cortex.jan.ai/docs/quickstart)
2. Run the model with:
    ```
    cortex run your_model_name
    ```

## Credits

- **Author:** [Original model creator]
- **Converter:** [Converting organization/person]
- **Original License:** [Link to original license]
- **Papers/References:** [Relevant papers or documentation]
```
4. Review and verify:

- Model license is correctly specified
- All URLs are valid and point to the correct resources
- Model names and commands are accurate

5. Click "Commit changes" to save the model card