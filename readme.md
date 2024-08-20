# **Commbank Savings Tool**
---

Gets the total sum of rounding up purchases to the nearest dollar for the last N-days. Calculate once a month to determine how much you need to transfer.

### **Installation**:

Requirements:
```sh
  pip install -r requirements.txt
  pip3 install -r requirements.txt
```

### **Persistent Files**:

  1. **./persist/** : saves all individual purchases / rounding for N-days. (Use: --save True to persist. Use: --persist to set the persistence directory)
  2. **./data.json** : Contains the amounts you need to transfer indexed by a datestring (format=dd-mm--yyyy) for the last N-days

### **CLI**:

  Run the following to get a full list of the CLI arguments

  ```sh
    python main.py --help
    python3 main.py --help
  ```