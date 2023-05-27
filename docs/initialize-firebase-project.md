## Create a firebase project in the browser
### Google account
You'll need a Google account to use firebase. You can create one here: 
https://www.google.com/account/about/

### Firebase Project
While logged in into your Google account head over to:
https://firebase.google.com/

- Click on `Get started`
- Click on the plus sign with `add project`
- name your project and click on `continue`
- For now, we don't use Google Analytics (you can leave it enabled if you want to use it in the future)
- Click 'Create project'

### Adding a webapp to your project
in your project console (in the firebase project), we now want to add an app to our project

- Click on `</>`
- name the app (can be the same as your project) and check `Also set up Firebase Hosting`
- Click on `Register app`
- Click on `Next`
- Click on `Next`
- Click on `Continue to console`

### Adding Firestore to your project
in your project console in the left hand menu click on build and select Firestore Database

- Click on `Create database`
- Leave `Start in production mode` selected and click on `Next`
- Select a Firestore location and click on `Enable`
- To see if everything is set up correctly, in the menu click on the gear symbol next to the Project overview and select `Project settings`
- Under `Default GCP recource location` you should see the Firestore location, you've selected.
  - If you don't see the location, select one now (click on the `pencil-symbol` and then on `Done` in the pop-up window)
