# **Commbank Savings Tool**
---

Gets the total sum of rounding up purchases to the nearest dollar for the last N-days. Calculate once a month to determine how much you need to transfer.

### **Installation**:

Requirements:
  - Preinstalled: conda, pip, python, anaconda
  

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

### **Deploying to your local WIFI network**:

1. create a file called .env
2. Copy and paste the following into .env:
```sh
    COMMBANK_USR_<YOUR_FIRST_NAME> = <YOUR_FIRST_NAME>
    COMMBANK_PWD_<YOUR_FIRST_NAME> = <YOUR_COMMBANK_PASSWORD>
```
3. Run the following command to initialize the server:
```sh
    python app.py
    python3 app.py
```
4. On your browser go to the following address: 192.XXX.X.X:8000