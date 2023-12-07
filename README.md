# CSC-899 : Personalized Resume Bullet Point Generator From Student Academic and Project Data

## Introduction:
This project automates the process of resume bullet point generation by extracting data from student’s Canvas account.<br />
By integrating the ChatGPT API, it generates impactful bullet points for resume based on this data.<br />
This project combines data gathering via APIs and web data scraping, applying NLP techniques to extract useful information from collected data and finally generating resume bullets points by integrating LLM like ChatGPT.

## Steps to follow:
### Step 1: Clone this git repo and use your respective code editor.
If you use VS Code, you can simply click on the icon below and click on clone repository and copy paste this http link: "https://github.com/hru952/CSC-899.git" <br />
![image](https://github.com/hru952/CSC-899/assets/124914776/fad95448-b7a9-41f1-b254-90c442af876e)
### Step 2: Generate Canvas API token
- Login to your SFSU student canvas account.
- Click on Account -> Settings -> Under Approved Integrations, click on + New Access Token <br/> ![image](https://github.com/hru952/CSC-899/assets/124914776/5b2836b7-43c8-491c-ad40-757ed499f7d9)
- The below box will open. Set the expires to 31st May and click on "Generate Token". <br/> ![image](https://github.com/hru952/CSC-899/assets/124914776/5e7cb961-8b9e-466f-865d-72a7fd4e5958)
- An access token will be generated and the following box appears. MAKE SURE TO COPY THIS API TOKEN. <br/> ![image](https://github.com/hru952/CSC-899/assets/124914776/3b7c20d1-1870-4a99-b5fd-af493593bd83)
- If you didn't copy the API token, simply repeat this process and generate a new API key and make sure to copy it.


