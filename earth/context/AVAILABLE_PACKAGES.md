# Available Python Packages in GA Execution Environment

## **CRITICAL CONSTRAINT**

**All code executed within the GA fitness evaluation environment MUST use only the packages listed below.**

This includes:
- `FitnessClass` and all its dependencies
- `FeatureBuilder` and data loading code
- Any helper modules imported by fitness code
- Scripts that generate code used in fitness evaluation

**DO NOT USE** packages not listed here, even if they are available in your local development environment.

---

## **Key Package Constraints**

### **Parquet Files**
- ✅ **USE**: `fastparquet` (available)
- ❌ **DO NOT USE**: `pyarrow` (not available)
- ✅ **USE**: `pd.read_parquet(path, engine='fastparquet')`

### **Distributed Computing**
- ❌ **DO NOT USE**: `dask` (not available)
- ✅ **USE**: Standard pandas operations or numpy for parallelization

### **Data Processing**
- ✅ **USE**: `pandas`, `numpy`, `scikit-learn` (all available)
- ✅ **USE**: Standard Python libraries

---

## **Complete Package List**

audioread==3.0.1
catboost==1.2.8
certifi==2025.4.26
cffi==1.17.1
charset-normalizer==3.4.2
contourpy==1.3.2
cramjam==2.10.0
cycler==0.12.1
decorator==5.2.1
fastparquet==2024.11.0
fonttools==4.58.0
fsspec==2025.3.2
graphviz==0.20.3
idna==3.10
joblib==1.5.0
kiwisolver==1.4.8
lazy-loader==0.4
librosa==0.11.0
lightgbm==4.6.0
llvmlite==0.44.0
matplotlib==3.10.3
msgpack==1.1.0
narwhals==1.39.0
numba==0.61.2
numpy==2.2.5
opencv-contrib-python-headless==4.11.0.86
packaging==25.0
pandas==2.2.3
pillow==11.2.1
platformdirs==4.3.8
plotly==6.0.1
pooch==1.8.2
pycparser==2.22
pydantic==2.12.5
pyparsing==3.2.3
python-dateutil==2.9.0.post0
pytz==2025.2
requests==2.32.3
scikit-learn==1.6.1
scipy==1.15.3
six==1.17.0
soundfile==0.13.1
soxr==0.5.0.post1
threadpoolctl==3.6.0
typing-extensions==4.13.2
tzdata==2025.2
urllib3==2.4.0
xgboost-cpu==3.0.1

---

## **Usage Examples**

### **Reading Parquet Files**
```python
# ✅ CORRECT
import pandas as pd
df = pd.read_parquet("data.parquet", engine="fastparquet")

# ❌ WRONG - will fail in GA environment
df = pd.read_parquet("data.parquet")  # defaults to pyarrow
df = pd.read_parquet("data.parquet", engine="pyarrow")
```

### **Data Processing**
```python
# ✅ CORRECT - use pandas/numpy
import pandas as pd
import numpy as np
df.groupby("col").agg({"val": "mean"})

# ❌ WRONG - dask not available
import dask.dataframe as dd
df = dd.read_parquet("data.parquet")
```