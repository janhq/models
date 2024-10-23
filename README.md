# Model Conversion Guide
This guide will help you understand how to convert AI models into different formats that our applications can use.

## What We're Doing
We convert AI models into special formats (GGUF, TensorRT, ONNX) so they can work with our applications called [Jan](https://github.com/janhq/jan) and [Cortex](https://github.com/janhq/cortex.cpp). Think of this like converting a video file from one format to another so it can play on different devices.

### New Model Conversion

#### Step 1: Create a New Model Template

1. Go to our model storage at: https://huggingface.co/cortexso
2. Click "New Model"
3. Give it the same license as the original model you're converting
4. Create two important files in your new model:

**File 1:** `model.yml`
This file tells our system how to use the model. Copy this template and fill in the details:

```
# Basic Information
id: your_model_name    # Choose a unique name
model: your_model_name # Same as above
name: your_model_name  # Same as above
version: 1             # Start with 1

# Model Settings
stop:                  # Where the model should stop generating
  - "<|eot_id|>"       # You might need to change this

# Default Settings (Usually keep these as they are)
stream: true
top_p: 0.9
temperature: 0.7
max_tokens: 4096

# Technical Settings
engine: llama-cpp      # The engine type
prompt_template: "<|begin_of_text|>..."  # How to format inputs
ctx_len: 8192          # Context length
ngl: 34                # Usually layers + 1
```

**Common Errors:**
- Wrong Stop Tokens: If the model keeps generating too much text, check the stop tokens in model.yml
- Engine Errors: Make sure you picked the right engine type in model.yml
- Template Issues: Double-check your prompt_template if the model gives weird outputs

**File 2:** `metadata.yml`

```
version: 1
name: your_model_name
default: 8b-gguf-q4-km
```

#### Step 2: Convert Your Model 🔄

1. Visit: https://github.com/janhq/models/actions
2. Choose your conversion type:
- For [GGUF](https://huggingface.co/docs/hub/gguf) format: Click `Convert model to gguf with specified quant`
- For [TensorRT](https://github.com/NVIDIA/TensorRT-LLM): Coming soon
- For [ONNX](https://onnx.ai/): Coming soon

3. Click `Run workflow` dropdown
4. Fill in the required information
5. Click `Run workflow` button to start the conversion

#### Step 3: Check If It Worked

1. Watch the conversion process (it looks like a loading bar)
2. If you see any errors ❌:
- Click on the failed step to see what went wrong
- Create a "Bug Report" on GitHub
- Contact Rex or Alex for help

#### Step 4: Final Testing 🧪
After the conversion completes:

1. Check Huggingface page to make sure all files are there
2. Test the model in Cortex:

- Make sure it generates text properly
- Check if it stops generating when it should

### Install

Using yarn:

```shell
yarn add @janhq/models
```

Using npm

```shell
npm i @janhq/models
```

### Import the package

```js
// javascript
const models = require("@janhq/models");

// typescript
import * as models from "@janhq/models";
```

```js
const MODEL_CATALOG_URL = models.default;

console.log(MODEL_CATALOG_URL);
// {
//   "id": "",
//   "name": "",
//   "modelUrl": "",
//   "versions": [
//      "downloadLink": "",
//     ...
//   ]
//   ...
// }
```
