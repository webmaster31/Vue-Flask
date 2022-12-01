# template-services
The Docker-based services template

## Configure Services

### 1. Configure Email Service using Mailjet
<details>
  <summary>Click here to see instruction</summary>

###### Steps:
1. Go to the [Mailjet website](https://www.mailjet.com/)
2. Signup for free.
3. Verify your api and secret key is working for sending emails with [get_started page](https://app.mailjet.com/auth/get_started/developer`)
4. Copy the API key and Secret key to the `.env.dev` file
    ```dotenv
    MJ_APIKEY_PUBLIC= # API key
    MJ_APIKEY_PRIVATE= # API secret key
    ```
5. Uploading/updating template to Mailjet:

   a. **Manual upload**

      i) Create the email template from [transactional page](https://app.mailjet.com/templates/transactional). Open `By coding it in HTML` and import HTML from file. Upload templates one by one from [services/templates folder](./services/templates).
      Please pay attention that you need to create separate email templates for welcome email and password reset email.

      ii) Save and Publish the Templates
   
   b. **Upload by script**

      i) Requires python3 and pip installed

      ii) Run `./scripts/update_mailjet.sh <stage>`

      iii) If everything works, you should be able to see in the terminal:

      ```
      Templates created successfully on Mailjet. Following are the template IDs:
      Junction-ResetPassword: 3850535
      Junction-Welcome: 3850536
      ```

8. Copy the template ID and update the `.env` file
    ```dotenv
    WELCOME_EMAIL= # template id of welcome email
    PASSWORD_RESET_EMAIL= # template id of reset password email
    ```
9. Set the following variables for email in `.env` file
   ```dotenv
   SENDER_EMAIL= # Sender email to be set in email
   SENDER_NAME= # Sender name to be set in email
   COMPANY_NAME= # Name of company to be set in email
   ```
###### Queue Name for email service
```
email
```
###### Task Name for email service
```
send_email
```

###### Message Format for email service
The email message need to be a dictionary with following keys and values type:

```json
{
    "email_data": {
        "email_type": str,
        "recipient_email": str,
        "recipient_name": str,
        "subject": str,
        "confirmation_link": str,
        "password_reset_url": str
    }
}
```
</details>


### 2. Configure Logging Service
<details>
  <summary>Click here to see instruction</summary>

   To enable logging go to [rollbar](https://rollbar.com/) and register a free account. During the setup Rollbar asks for programming language. Choose any you like and copy from the code `access_token`.
<br><br>Another way to retrieve `access_token` is to create a Project, then go to the Projects menu -> Project Access Tokens and copy the one called `post_server_item`.
<br>
   ```dotenv
   ROLLBAR_ACCESS_TOKEN= # token copied from step described above
   ```
</details>

### 3. Configure Pusher
<details>
   <summary>Click here to see instruction</summary>

Please create an account and get the keys as described in [instruction](https://pusher.com/docs/) (Channels -> Getting Started).
Fill the following .env variables:
``` dotenv
PUSHER_APP_ID=
PUSHER_API_KEY=
PUSHER_API_SECRET=
PUSHER_CLUSTER=
```
The .env variables `PUSHER_APP_ID` and `PUSHER_CLUSTER` should match the same variables from [vue](https://github.com/EcorRouge/vue-flask-templates/vue) repository.

</details>

### 4. Configure Social Auth
<details>
   <summary>Click here to see instruction</summary>

#### 4.1 Configure Google OAuth
* Log into [Google Cloud Platform Console](https://console.cloud.google.com/apis/credentials).
* Click the `Select a Project` dropdown or Click `New Project Button`.
* Give it a project name that you want (e.g. Template Project)
* Once the project is created (takes a few seconds), use the project selector again and pick created project
* On the left, click `Credentials` then click consent screen.
* Note: If this is your first time creating a client ID, you can also configure your consent screen by clicking `Consent Screen`.  You won't be prompted to configure the consent screen after you do it the first time.
* On next screen add `Name`, `User support email address` and `developer email address` then click `save and continue` button.
* Scopes Screen select scope api `/auth/userinfo.email` and `/auth/userinfo.profile` the click `save and continue` button.
* On the next screen select `Web application` as `Application type` and give it a name.
* Add `http://localhost:8080` (running port) into the `Authorized JavaScript origins` and click the `Create` button.
* Click back to `Credentials` tab and select `oAuth Client Id`.
* Finally, you will get a popup containing your `Client ID` and `Client Secret`. Copy those values.
* Update GOOGLE_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET into `.env.dev` file.

* https://user-images.githubusercontent.com/42783505/141343278-64192daa-28f6-4c3e-b0b1-59f51a584841.mp4

#### 4.2 Configure Github OAuth
See [Configuration Reference](https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app)
* Set `Homepage URL` as `http://localhost:8080` 
* Set `Authorization callback URL` as `http://localhost:8080/session/github/oauth`
* Update GITHUB_CLIENT_ID and GITHUB_OAUTH_CLIENT_SECRET into `.env.dev` file.

#### 4.3 Configure Linkedin OAuth

* Go to the [LinkedIn developer site](https://developer.linkedin.com/) and click the `Create App` button on the banner.
* Select an existing company or choose a New Company. If you select the new company, you will be asked to enter a company name. 
* On next screen fill the form:
  * App Name,
  * Linkedin Page Url (Please create new if you've no existing page),
  * upload logo
  * and click on create app button.
  * Go to the Auth section and add Redirect URLs. ![Authentication _](https://user-images.githubusercontent.com/42783505/141883872-b8605ca0-7156-446f-af35-bb1ba66bf5e9.png)
  * Go to the Products tab, select and add Sign In with LinkedIn to your products.
  ![Products _ App d](https://user-images.githubusercontent.com/42783505/141883554-4859f74e-9805-462c-b80c-1c149eeedecd.png)
  * Return to Auth tab and wait for a few seconds for it to appear in 0Auth 2.0 scopes.
  ![Auth-scopes](https://user-images.githubusercontent.com/42783505/141883526-87fdb199-e6f5-4d8f-b970-71fa7716f7b4.png)
* Update LINKEDIN_CLIENT_ID and SOCIAL_AUTH_REDIRECT_URI=http://localhost:8080/session/social/oauth (Update if running on different port and please add same url to linkedin when creating/updating app)
into `.env.dev` file

#### 4.4 Configure Facebook OAuth

Facebook configurations are described and used in [vue](https://github.com/EcorRouge/vue-flask-templates/vue)

</details>

## Launch Entire System
1. Clone all repos `[ flask, services, vue ]` inside a directory eg `vue-flask-templates`


2. Go to folder `services` inside `vue-flask-templates`


3. 
   * Copy `services/scripts/sample.env` to `services/sample.env` and name it as: `<env>.env`. 
   * Fill in all empty variables in the `services/<env>.env`
      <br><br>
      The variable definition is given in [the description of Env variables](#env-variables) and in README files in [flask](https://github.com/EcorRouge/vue-flask-templates/flask) and [vue](https://github.com/EcorRouge/vue-flask-templates/vue).

4. Run the `run.sh` bash script. The script takes two named arguments:
   
   a. `--env`: The env name provided should be same as the env filename created in step 3.
   b. `--run-ui`: Default value if not provided is false
   
   ```
   Usage: run.sh [-e env] [-u run-ui]
      -e, --env             Environment to run (dev, test, production)
      -u, --run-ui          Run UI app (Optional argument)(Default Value: false)

   Example: bash run.sh --env test --run-ui true
   ```

## Reset the entire system
1. Go to folder `services` inside `vue-flask-templates`


2. Run the `reset-system.sh` bash script. The script takes `no argument`. After run, it will show warning and prompt user for `yes` or `no`. Enter `Y or y` for YES and `N` or `n` for NO.
   ```
   Example: bash reset-system.sh
   ```


## Run services manually
<details>
   <summary>Click here to see instruction</summary>

### 1. Copy the `.env.dev` file to `.env` file
### 2. Fill in the empty variables in `.env`
   as described in [the description of Env variables](#env-variables) section.
### 3. Check local services
If Mysql or RabbitMQ are running locally on your machine, please stop them before going to the next step.
 You may use these commands (checked on Ubuntu):
   <br>
   ```
   sudo /etc/init.d/mysql stop
   sudo -u rabbitmq rabbitmqctl stop
   ```
   You may need to use your own RabbitMQ user after -u flag.

### 4. Run services
From the root folder of `services` run 

 ```shell
 docker-compose -f docker-compose.yml up -d
 ```

### 5. Setup UI

For UI run `vue` according to README in [vue](https://github.com/EcorRouge/vue-flask-templates/vue)
</details>

## Env Variables
1. RabbitMQ Configs
   ```dotenv
   RABBITMQ_USER= # user through which we communicate with rabbitmq
   RABBITMQ_PASSWORD= # user's password
   RABBITMQ_VHOST= # virtual host 
   BROKER_PATH= # RabbitMQContainerName:PORT
   MQ_EXCHANGE= # Name of Exchange
   ```
2. MySQL Configs
   ```dotenv
   MYSQL_ROOT_PASSWORD= # root user's password
   MYSQL_USER= # user to communicate to mysql db
   MYSQL_PASSWORD= # user's password
   MYSQL_DATABASE= # mysql database we use
   MYSQL_HOST = # Name of mysql container
   ```
3. Email Configs

   ```dotenv
   SENDER_EMAIL= # Email from which we send the email to user
   SENDER_NAME= # The sender's user name
   COMPANY_NAME= # Name of company for example: template company to use in email template
   WELCOME_EMAIL= # welcome email's template ID
   PASSWORD_RESET_EMAIL= # reset email's template ID
   MJ_APIKEY_PUBLIC=
   MJ_APIKEY_PRIVATE=
   ```
4. Rollbar Configs
   <br>
   ```dotenv
   ROLLBAR_ACCESS_TOKEN=
   ```



## Docker Commands
<details>
  <summary><b>Click here to see the docker commands</b></summary>

1. Docker Compose Up to create images and run containers of all services
    ```shell
    docker-compose -f docker-compose.yml up -d
    ```
2. List docker images with
    ```shell
    docker image ls
    ```
3. List running docker containers
    ```shell
    docker ps
    ```
4. List all containers (stopped and running)
   ```shell
    docker ps -a
   ```
5. View logs of specific container
    ```shell
    docker logs -f <containerID>
    ```   
6. Run a command in a running container
    ```shell
    docker exec -it <containerID> <command eg bash or sh>
    ```
7. Stop docker container
    ```shell
    docker stop <containerId>
    ```
8. Remove stopped container   
    ```shell
    docker rm <containerId>
    ```
9. Remove docker image
    ```shell
    docker rmi <imageId>
    ```
</details>
