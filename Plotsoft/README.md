# PDFill Free (x64) AutoPkg recipes
**download** (get the actual installer)  
**build** (transform hte MSI for corporate distribution)  
**BMS** (import the package into baramundi server)

**Features:**  
Installs per machine.
Auto updater is disabled.  

To use the baramundi import recipe,<br>
the following varibles need to be specified in the AutoPkg config.json file:<br>
  ```"BMS_IMPORT_OU_GUID": "11111111-ABCD-1234-ABCD-12345678ABCD",
  "BMS_IMPORT_PATH_TST": "\\\\domain\\path",
  "BMS_SERVER1": "server.domain.tld",
  "BMS_SERVER_PORT": "443",
  "BMS_USERNAME": "domain\user",