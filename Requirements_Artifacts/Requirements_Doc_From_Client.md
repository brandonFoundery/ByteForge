I want to build an app that will deploy to azure.  The main purpse is to migrate data from one system to another in the background, but it will have a UI component which I would like for it to be inclusive to make it easy to deploy.  
The UI, it would be nice to be a controller with javascript or something that is cool and snazzy.  I want a top panel that shows the from system and pipe connecting it to the to system.  On the From side, I would like to show a barel that represents the progress bar and as the records are moved it will update the barel to show it slowly draining.  I also want an animation showing th pipe flowing with maybe a barber shop pole animation.
The bottom half of the panel should show the mapping from the from side to the to side.  I will provide more on this but for now there are about 10 fields that need to be mapped and then a go button.
There must be a login page and security to protect the site.
The from and two will be different connections.  The from will be an api, so we will need a api key.  The two will be an api as well with a different connection key.
The keys should be stored in the azure key vault.
The app should log to logentries using nlog or log4net.
The to location will always have a tenant ID in addition to a server name.  Each servername will require a separate api key.
The app can be fired off and then left and returned later to show the status of the conversion.  So there needs to be a processes page that shows the history and the status of on going conversion.  Clicking on a row will take you to the view described above to view the progress.  

Think about this carefully.  Review your solution once you are done and determine if it is sufficient or needs modification.  Give a FULL and verbose design to implement this.

Use Authentication 
Show a one page mapping
Field Mapping is a Tenant Based Mapping
Filter:
- select the IDs that are to be moved (based on the Filter Type)


mapping_fields.xlsx - is a per tenant team
Source -> Dest (with the ability to re-map to a different field)


Authentication from LSO and LSC
Endpoints

Chad Roseburg - as the endpoint info and API keys

LSO and LSC in aws

Timeline:   May

Hi Brandon/Chad,

I meant to get this out yesterday, however; I got tied up in a meeting that went extremely long. Sorry about that.

Brandon please meet Chad, Chad meet Brandon...

As discussed, we have an automation project to automate pushing data from LSO to LSC. This project has been ongoing, but will make critical improvements in terms of time/productivity as well as accuracy of data transfers. Further, it will allow other teams to leverage and reduce the amount of effort Technical Services needs to perform - so we can focus on other activities that let us work at higher opportunity costs.

Project
UI: We have quickly written an example UI/Process which are the steps we would follow to perform the process itself. (Attached for reference)
XLXS Files: We attached two examples. One is a spreadsheet which creates the mapping fields in the UI and the other is IF a spreadsheet is uploaded to provide a specific list of UUID's. (Refer to UI example)

APIs: There is a LSO and LSC APIs which allow the data automation to be completed. @Chad Roseburg Please ensure Brandon has access to both of these. (NOTE: LSO has IP whitelisting access, so we need to consider this and get Brandon access. Brandon, we should ensure that the final solution allows for authentication and access to this via server, rather than having to whitelist every single user that authenticates.

Basic Application
Similar/Simple UI (like example)
Add Authentication with username and password. *Need to ensure it is locked down for security so may want MFA or other simple/quick options to ensure.
LSO to LSC Data automation
Logging

@Chad Roseburg @Brandon Shuey Please work together to as quickly as you can to get this off the ground. We need to make some quick progress as possible.

Thanks,
Tim






Duval - credentials
Matt - access to QA

Client is a Python Code

Test Environments - IP whitelisted (Give to Chad)

LSO data needs to be scrubbed because everything is a string
- Dates - if null they will write "silent" or "N/A", return string.Empty or Null or None
- Numbers - TryParse


