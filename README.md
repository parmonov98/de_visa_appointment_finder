# German VISA Appointment Vacancy Finder

This application automates looking for a particular type of German 🇩🇪 VISA appointment for Indian 🇮🇳 citizens. It was written mostly to suit my needs but is easily configurable.
It repeatedly checks for the appointment with some delay. When it finds an appointment, it sends an alert via your GMail to your preferred recipient so that they can book an appointment as soon as possible.

## Setup
1. create/login to gmail account and [create a new app password](https://www.lifewire.com/get-a-password-to-access-gmail-by-pop-imap-2-1171882) for our app
2. create an account at [VFS](https://visa.vfsglobal.com/ind/en/deu/register) if you haven't yet done so.
3. fill in the values in the `.env` file which would contain important credentials such as:
    - username, password for logging into the VFS site
    - sender's & receiver's email id (to send the alert)
    - app password generated above.

   Here's how a sample `.env` file looks like:
   ```
   VFS_USERNAME='max_mustermann@gmx.de'
   VFS_PASSWORD='...'
   ...
   ```
4. Install dependencies.
    - `pip install -r requirements.txt` OR
    - `conda env create -f env.yml`
5. run `python appointment_finder.py &`
    - this would run in the background and sends an alert when an empty slot is found, containing the date of the available appointment.

Good Luck!
