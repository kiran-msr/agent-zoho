Env: test_rig
IP : 192.168.82.10
ssh root@msr@2025

1. Installing uv
# curl -LsSf https://astral.sh/uv/install.sh | sh

2. Setting Up Env:
# uv run manager.py

3. add python-dotenv package in to the project(if not already present)
# uv add python-dotenv

4. Create a new project viz. whatsapp-zoho-ticket in google cloud console with e-mail msritsolution.dev@gmail.com (password: msrdev@1234#) and enable the Vertex AI service. Attach this project with proper billing account.

5. Create .env file in the project root directory 
=> Create a .env file with vi editor and the llowing properties:
GCLOUD_PROJECT_ID=whatsapp-zoho-ticket 
GCLOUD_LOCATION=us-central1 => chosen as suggested in website
 
=> for ZOHO related property values, see sections 21 below:
ZOHO_CLIENT_ID=1000.QUE3MRNZOIVOOGO2VLLOXOY1Y1J1YY
ZOHO_CLIENT_SECRET=48a0f8f81155c7d7fe0bfa8ffe13c268a5b8c973d0
 
ZOHO_REFRESH_TOKEN=1000.0c4c93531bf6abb8c6308497c9eab73b.db7b4058eb356bea36b326951c4749b4
ZOHO_ORG_ID=60045605535
ZOHO_DEPARTMENT_ID=217214000000010772
ZOHO_CONTACT_ID=217214000000287366
ZOHO_BASE_URL=https://desk.zoho.in/api/v1
ZOHO_TOKEN_URL=https://accounts.zoho.in/oauth/v2/token
ZOHO_SCOPE=Desk.tickets.CREATE,Desk.tickets.READ,Desk.basic.READ,Desk.settings.READ,Desk.contacts.READ
ZOHO_ACCESS_TOKEN=1000.cc09cfe4f23df6adf439c84f41e5a53d.532b642f3076805759c3ba7238ec44e9

6. Fetch the Gemini API key from Google AI Studio (AIzaSyDHvLLwnL2x8yvdD18xZdCUNzW3oOHo6qs)

7. run following command to export GEMINI_API_KEY in console terminal
export GEMINI_API_KEY="AIzaSyDHvLLwnL2x8yvdD18xZdCUNzW3oOHo6qs" 

8. Install Google Cloud CLI - run the following commands in particular location (e.g. /usr/local)
# curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-492.0.0-linux-x86_64.ta…
# tar -xf google-cloud-cli-492.0.0-linux-x86_64.tar.gz
# ./google-cloud-sdk/install.sh
# exec -l $SHELL
  
9. Login in Google Cloud CLI - this is required for calling google cloud related APIs (here from outline_llm.py)
# gcloud auth application-default login

10. We had to update whatsapp MCP bridge as we needed to handle the version mismatch issue

11. Install GO & UV
# which uv (to find the installed location of uv & note it)

12. We have used the following project name for Whatsapp MCP server
lharries/whatsapp-mcp: WhatsApp MCP server
(github url : https://github.com/lharries/whatsapp-mcp.git) - clone it a particular location (e.g. /usr/local/whatsapp-mcp)
two dirs will be created -> for MCP server /usr/local/whatsapp-mcp/whatsapp-mcp-server
						 -> for bridge server /usr/local/whatsapp-mcp/whatsapp-bridge

13. To correct version mismatch used the following command:
# go get go.mau.fi/whatsmeow@latest
# go mod tidy

14. we have change some code in main.go inside it
 
Old call								New call
---------------------					----------------------------------------							
client.Download(media)					client.Download(ctx, media)
sqlstore.New(dbType, dsn, logger)		sqlstore.New(ctx, dbType, dsn, logger)
container.GetFirstDevice()				container.GetFirstDevice(ctx)
client.Store.Contacts.GetContact(jid)	client.Store.Contacts.GetContact(ctx, jid)

declared globally:
var ctx = context.Background()

15. Run the WA MCP server (from within /usr/local/whatsapp-mcp/whatsapp-bridge/):
# go run main.go

16. When whatsapp mcp bridge is up and running a qr code will be shown scan the qr code with receiver whatsapp link device scanner.

17. Go to the root path of the project (/usr/local/smartler_whatsapp_automation)

18. open the whatsapp_agent.py  to change the hardcoded phone number to the sender WA phone number or WA group name

19. also update the installed uv path and mcp-server main.py path in Agent initialisation code

whatsapp_agent = Agent(
        instructions="Whatsapp Agent",
        llm="gemini/gemini-2.0-flash",
        tools=MCP(
            command="/root/.local/bin/uv",  // uv path
            args=["--directory","/usr/local/whatsapp-mcp/whatsapp-mcp-server","run","main.py"] // mcp-server main.py path
        ))
		
20. run command uv run whatsapp_agent.py  (to test the whatspp get message operation)

21. Now Start configuring ZOHO....

	a. zoho developer account is reuquired with zoho desk service enabled. 
	b. In ZOHO portal create a "Server Based Application" and get the client id and client secret after providing the Client Name (any name), Homepage URL (any, eg. http://localhost:8050) & Authorised Redirect URL (http://localhost:8050/success).
	c. hit the following url with client id in browser		https://accounts.zoho.in/oauth/v2/auth?response_type=code&client_id=<CLIENT_ID>&scope=Desk.tickets.CREATE,Desk.tickets.READ,Desk.basic.READ,Desk.settings.READ,Desk.contacts.READ&access_type=offline&redirect_uri=http://localhost:8050/success&state=-5466400890088961855
	d. accept it (you will need to login to zoho, if not already done)
	e. it will redirect to http://localhost:8080/success?state=-5466400890088961855&code=1000.64aff69f1a45e483b91a6c033796691e.35a35e2e46c1d7208d87bdcc762e86dd&location=in&accounts-server=https%3A%2F%2Faccounts.zoho.in&
	f. note the calue of the "code" param (here, 1000.64aff69f1a45e483b91a6c033796691e.35a35e2e46c1d7208d87bdcc762e86dd). this code will be needed to generate access token.
	g. to generate the access token
	curl --location --request POST 'https://accounts.zoho.in/oauth/v2/token?code=<GET_FROM_ABOVE>&grant_type=authorization_code&client_id=<CLIENT_ID>&client_secret=<CLIENT_SECRET>&redirect_uri=http%3A%2F%2Flocalhost%3A8050%2Fsuccess' \
--header 'Cookie: _zcsr_tmp=44039e40-a734-4ce7-8445-0026b966dbf0; iamcsr=44039e40-a734-4ce7-8445-0026b966dbf0; zalb_6e73717622=13e67ac15bc4d3ece130966123511df7'
	h. get the access_token and refresh_token from the response:
	{
		"access_token": "1000.cc09cfe4f23df6adf439c84f41e5a53d.532b642f3076805759c3ba7238ec44e9",
		"refresh_token": "1000.b5fbb6ec90839c8fe22c4642d1c14263.b5e6f07a03b8e641ccded5e4fc1b5663",
		"scope": "Desk.tickets.CREATE Desk.tickets.READ Desk.basic.READ Desk.settings.READ Desk.contacts.READ",
		"api_domain": "https://www.zohoapis.in",
		"token_type": "Bearer",
		"expires_in": 3600
	}
	i. set the value of ZOHO_REFRESH_TOKEN and ZOHO_ACCESS_TOKEN in .env file. The access token is also used to get the organizationId,contactId,depratmentId 
	
	organizationId:
	curl --location 'https://desk.zoho.in/api/v1/organizations' \
	--header 'Authorization: Zoho-oauthtoken 1000.0c8d68e86ae440ddc3cd3e4d9cc1abfa.81bac1fe33afbbc368fb816dca1ed155' \
	--header 'Cookie: _zcsr_tmp=002492ae-ae54-41b9-a497-43bc85450586; crmcsr=002492ae-ae54-41b9-a497-43bc85450586; zalb_2eed0b67fd=bd8e9abd8c1adc3d06fe29251875e998; zd_group_name=c8fbcc98113e2f7d4d3d2021a6072dab47116094892fc8ae14c9762426648080'
	
	departmentId:
	curl --location 'https://desk.zoho.in/api/v1/departments' \
	--header 'Authorization: Zoho-oauthtoken 1000.691ab19bec03768fcde567e2b6ee5505.aaba706654918b2bb681ccf0cacdd318' \
	--header 'Cookie: _zcsr_tmp=002492ae-ae54-41b9-a497-43bc85450586; crmcsr=002492ae-ae54-41b9-a497-43bc85450586; zalb_2eed0b67fd=bd8e9abd8c1adc3d06fe29251875e998; zd_group_name=c8fbcc98113e2f7d4d3d2021a6072dab47116094892fc8ae14c9762426648080; _zcsr_tmp=002492ae-ae54-41b9-a497-43bc85450586; crmcsr=002492ae-ae54-41b9-a497-43bc85450586; zalb_2eed0b67fd=bd8e9abd8c1adc3d06fe29251875e998; zalb_b63c18cf33=959f91c134c528666fdf824b0c606682; zd_group_name=db5641caa4df2fe898954525985a60e153c3f3904d066d400535d11876207ca2'

	contactId:
	curl --location 'https://desk.zoho.in/api/v1/contacts' \
	--header 'Authorization: Zoho-oauthtoken 1000.691ab19bec03768fcde567e2b6ee5505.aaba706654918b2bb681ccf0cacdd318' \
	--header 'Cookie: _zcsr_tmp=002492ae-ae54-41b9-a497-43bc85450586; crmcsr=002492ae-ae54-41b9-a497-43bc85450586; zalb_2eed0b67fd=bd8e9abd8c1adc3d06fe29251875e998; zd_group_name=c8fbcc98113e2f7d4d3d2021a6072dab47116094892fc8ae14c9762426648080; _zcsr_tmp=002492ae-ae54-41b9-a497-43bc85450586; crmcsr=002492ae-ae54-41b9-a497-43bc85450586; zalb_2eed0b67fd=bd8e9abd8c1adc3d06fe29251875e998; zalb_b63c18cf33=959f91c134c528666fdf824b0c606682; zd_group_name=db5641caa4df2fe898954525985a60e153c3f3904d066d400535d11876207ca2; _zcsr_tmp=002492ae-ae54-41b9-a497-43bc85450586; crmcsr=002492ae-ae54-41b9-a497-43bc85450586; zalb_2eed0b67fd=bd8e9abd8c1adc3d06fe29251875e998; zalb_b63c18cf33=959f91c134c528666fdf824b0c606682; zd_group_name=db5641caa4df2fe898954525985a60e153c3f3904d066d400535d11876207ca2'
	
	j. set the values of other properties in .env file viz. ZOHO_ORG_ID, ZOHO_DEPARTMENT_ID, ZOHO_CONTACT_ID

	k. other values in .env files are

	ZOHO_BASE_URL=https://desk.zoho.in/api/v1
	ZOHO_TOKEN_URL=https://accounts.zoho.in/oauth/v2/token
	ZOHO_SCOPE=Desk.tickets.CREATE,Desk.tickets.READ,Desk.basic.READ,Desk.settings.READ,Desk.contacts.READ
	
	l. open the manager.py and set the following values:
	TEST_PHONE_NUMBER = "<phone number field from the response of get /contacts zoho api>"
	numbers = ["Test group", "Test group 2"] // phone no or Group Name in WA
	
22. now run the main file (manager.py) of our project  
# uv run manager.py
	
	

	
	

