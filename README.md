# Test Time Scaling with Thought Graph Traversal

<div align="center">
<h4>
  📃 <a href="https://arxiv.org/abs/xxxx.xxxxx" target="_blank">arXiv Preprint</a>
</h4>
</div>

<div align="center">
  <h4>
    📦 <a href="https://drive.google.com/file/d/1c0BXEuDy8Cmm2jfN0YYGkQxFZd2ZIoLg/view?usp=sharing" target="_blank">IU X-Ray</a> • 📦 <a href="https://physionet.org/content/mimic-cxr/2.0.0/" target="_blank">MIMIC-CXR</a>
  </h4>
</div>

This repository contains the code for our paper, "Simple Radiology VLLM Test-time Scaling with Thought Graph Traversal."

We propose a training-free approach to enhance the reasoning capabilities of **Vision-Language Large Models (VLLMs)** for radiology report generation. By integrating a **Thought Graph Traversal (TGT)**, our method enables frozen radiology VLLMs to self-correct and produce more accurate and consistent chest X-ray reports.

---

## 🚀 Features

* **Training-Free Performance Boost**: Significantly improves VLLM reasoning for radiology report generation through test-time scaling, without requiring any model retraining.
* **Thought Graph Traversal (TGT)**: Introduces a lightweight TGT framework that guides the model to reason through organ-specific findings in a medically coherent order, enabling deeper and more logical analysis.
* **Reasoning Budget Forcing**: Dynamically adjusts the model's inference depth by extending its generation process at test time, further enhancing reasoning.
* **Outperforms Baselines**: Achieves superior performance compared to baseline prompting approaches on standard benchmarks.
* **Open-Sourced**: All code and prompts are open-sourced for full reproducibility.

---

## 🛠️ Setup

### **Before You Start**

Before setting up your environment and running the code, you'll need to obtain your API keys:

You'll need API keys for the large language models.
* For **OpenAI API Key**: Apply for one at [https://platform.openai.com/](https://platform.openai.com/).
* For **Aliyun API Key** (for Qwen-2.5-VL): Apply for one at [https://bailian.console.aliyun.com/](https://bailian.console.aliyun.com/).

### Environment Preparation

We recommend using `conda` for environment management:

```bash
# Create a virtual environment with the specified Python version
conda create -n tgt_vllm python=3.11.11
conda activate tgt_vllm

# Install PyTorch (ensure it matches the specified version)
pip install torch==2.1.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 # Adjust cu118 if your CUDA version is different

# Clone the repository
git clone https://github.com/glerium/Thought-Graph-Traversal.git
cd Thought-Graph-Traversal

# Download the model parameters for HuatuoGPT-Vision-7B
huggingface-cli download FreedomIntelligence/HuatuoGPT-Vision-7B --local-dir .

# Install dependencies
pip install -r requirements.txt
````

-----

## 📖 Usage

### Datasets

We use two datasets, **IU X-Ray** and **MIMIC-CXR**, in our paper.

  * **IU X-Ray**: You can download the dataset from [here](https://drive.google.com/file/d/1c0BXEuDy8Cmm2jfN0YYGkQxFZd2ZIoLg/view?usp=sharing). After downloading, please put the files in the `data/iu_xray` directory.
  * **MIMIC-CXR**: This dataset requires access permissions. Please apply for access from [PhysioNet](https://physionet.org/content/mimic-cxr/2.0.0/) first. Once you have permission, you can download the dataset from [here](https://drive.google.com/file/d/1DS6NYirOXQf8qYieSVMvqNwuOlgAbM_E/view?usp=sharing). After downloading, please put the files in the `data/mimic_cxr` directory.

-----

### Step-by-Step Guide

Follow these steps to run the inference:

#### 1\. Generate Expert Database

First, you need to adjust several variables in `config.json` to make sure the `prework.py` can work correctly. 

```json
{
  "proxy": {
    "use_proxy": true,
    "proxy_url": "http://your.proxy.url/"
  },
  "api": {
    "openai-apikey": "your-api-key-here"
  }
}
```

Before running `prework.py`, you need to generate a JSON file named `data.json` out of the IU-X-Ray/MIMIC-CXR dataset. This file should include the study IDs and reports for the training set from the dataset, formatted as follows:


```json
{
  "train": [
    {
      "study_id": "the_study_id",
      "report": "the report from the IU-x-ray/MIMIC-CXR dataset"
    },
  ]
}
```

Then, you need to run `generate_database/prework.py` to generate the `expert_database.json`. This step is crucial for preparing the necessary data for the main prediction process.

```bash
python generate_database/prework.py
```

After running `prework.py`, you'll generate `expert_database.json` in the `generate_database` directory. While you can format this file to match the structure of `predict/prompts/prompt_organ.json`, **for your convenience, you can also directly use the existing `prompt_organ.json` file already provided in `predict/prompts`**.

#### 2\. Configure Parameters in `predict/main.py`

Before running `predict/main.py`, you **must adjust several Python variables** directly within the `main.py` file to match your setup and desired experiment configuration.

Open `predict/main.py` and modify the following lines. Note that `main.py` will internally use these Python variables to set the necessary environment variables for `evaluate.py` before execution.

```python
# --- IMPORTANT: Adjust these parameters before running ---
num_loops = 1 # Number of times to repeat the experiment.

script_to_run = "evaluate.py" # Script for evaluation (usually remains as is)

output_dir = "logs" # This directory is used for general logging.

bot_type = 'huatuo' # Choose your desired VLLM type.
                    # Supported types are: 'huatuo', 'gpt-4o', 'qwen2.5-vl'.

# API keys for large language models. Replace 'your-api-key-here' with your actual keys.
# Only necessary for the bot_type you select.
openai_api_key = 'your-api-key-here'
aliyun_api_key = 'your-api-key-here'

# Path to your image data.
# For MIMIC-CXR:
# data_path = 'data/mimic_cxr'
# For IU X-Ray
data_path = 'data/iu_xray' # Adjust this to where you put your IU X-Ray images

# Path to the ground truth reports CSV file.
# Adjust this based on which dataset you are using and where your gts_*.csv file is located.
# For MIMIC-CXR
gts_path = 'gts_mimic.csv'
# For IU X-Ray
gts_path = 'gts_iuxray.csv'
```

Ensure `data_path` points to the correct location of your downloaded dataset images and `gts_path` points to the corresponding ground truth CSV file.

#### 3\. Run Prediction

After configuring the parameters in `main.py`, execute `predict/main.py` to start the prediction process:

```bash
python predict/main.py
```

The final experiment results will be saved in the `./outputs/` directory. You'll find two main types of files for each loop and bot type:

  * **`metrics_{LOOP}_{BOT_TYPE}.csv`**: Contains the evaluation metrics.
  * **`answers_{LOOP}_{BOT_TYPE}.csv`**: Contains the LLM's generated outputs.

-----

## 🤝 Contributing

We welcome contributions to this project\! If you have any questions, suggestions, or would like to submit a pull request, please feel free to open an issue on GitHub or contact us on yue.yao@anu.edu.au directly!

-----

## 📄 License

This project is licensed under the [MIT License](https://mit-license.org/).

-----

## 📚 Citing Our Work

If you find our work useful, please consider citing our paper:

```bibtex
@article{yao2025radiology,
  title={Simple Radiology VLLM Test-time Scaling with Thought Graph Traversal},
  author={Yao, Yue and Wen, Zelin and Tong, Yan and Tian, Xinyu and Li, Xuqing and Ma, Xiao and Xu, Dongliang and Gedeon, Tom},
  journal={arXiv preprint arXiv:XXXX.XXXXX}, 
  year={2025}
}
```
