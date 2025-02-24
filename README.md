# **Wildventures**: campervan_rentals

## Development

# [campervan_rental](https://campervan-rental-923a0b226ad3.herokuapp.com)

[![GitHub commit activity](https://img.shields.io/github/commit-activity/t/Maxcode0101/campervan_rental)](https://www.github.com/Maxcode0101/campervan_rental/commits/main)
[![GitHub last commit](https://img.shields.io/github/last-commit/Maxcode0101/campervan_rental)](https://www.github.com/Maxcode0101/campervan_rental/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/Maxcode0101/campervan_rental)](https://www.github.com/Maxcode0101/campervan_rental)


Wildventures represents a campervan rental business. The intention is to target adventure seekers and outdoorlovers who are into camping and roadtrips. The web based booking application allows users to gather informations about the available campervans, create an account, create a booking, and then manage, edit or delete their bookings. This site was developed using Python (Django), HTML, CSS and stores data in a PostgreSQL database.

**Site Mockups**
*([amiresponsive](https://ui.dev/amiresponsive?url=https://campervan-rental-923a0b226ad3.herokuapp.com)

![screenshot](documentation/readme/mockup.png)

source: [campervan_rental amiresponsive](https://ui.dev/amiresponsive?url=https://campervan-rental-923a0b226ad3.herokuapp.com)

> [!IMPORTANT]
> The examples in these templates are strongly influenced by the Code Institute walkthrough project called "I Think Therefore I Blog".

## UX

### The 5 Planes of UX

#### 1. Strategy Plane
##### Purpose
- Provide blog owners with tools to create, manage, and moderate engaging blog content and user interactions.
- Offer users and guests an intuitive platform to explore, engage, and contribute to blog discussions.

##### Primary User Needs
- Travellers need a reliable campervan that fits their needs (for instance, 4x4 drive, certain capacity etc.)
- Registered users need the ability to create, update, manage and delete a booking.
- Guests need the ability to browse and filter different campervans, gather information about the business and the rental conditions, and contact the service team.

##### Business Goals
- Rent out campervans for profit
- Give users the possibility to easily find a vehicle that fits their needs by dynamic filtering
- Make sure that users are having easy access to all of the informations regarding the rental process
- Providing a easy to handle booking management system

#### 2. Scope Plane
##### Features
- A full list of [Features](#features) can be viewed in detail below.

##### Content Requirements
- Booking management system (create, update, delete, and preview).
- Comment moderation and management tools.
- User account features (register, log in, log out, change Email/Password).
- Notification system for booking/payment and change- or cancel booking confirmations.
- 404 error page for lost users.

#### 3. Structure Plane
##### Information Architecture
- **Navigation Menu**:
  - Links to Home/About Us, Contact Page, FAQ's, Our Campervans, User Dashboard, Manage my Bookings, User Profile, Login/Register
  
- **Hierarchy**:
  - Campervan list displayed prominently for easy browsing.
  - Clear call-to-action buttons for all functionalities regarding account- and booking management.

##### User Flow
1. Guest users browse and filter campervans.
2. Guest users register for an account → sign up / log in to create a reservation. → Receive a approval notification.
3. Registered users can change dates or cancel their pending booking (reservation) → receive a approval notification.
4. Registered users pay for their reservation → receive a approval notification.
5. Registered users request a date change or cancelation of their aproved booking → receive a approval or notification.

#### 4. Skeleton Plane
##### Wireframe Suggestions
- Wireframes have not been used.

#### 5. Surface Plane
##### Visual Design Elements
- **[Colours](#colour-scheme)**: see below.
- **[Typography](#typography)**: see below.

### Colour Scheme

I used [coolors.co](https://coolors.co/fbfd4d-544c49-37422f-b2b04c-fdfec1) to generate my color palette.

- `#FBFD4D` main branding / logo.
- `#37422F` primary highlights.
- `#FDFEC1` secondary text.
- `#544C49` secondary highlights.

![screenshot](documentation/readme/coolors.png)

### Typography

- [Font Awesome](https://fontawesome.com) icons were used throughout the site, such as the social media icons in the footer.

## User Stories

### Agile Methodology

This project was developed using the Agile methodology. All user stories implementation progress was tracked through Github projects Kanban Board which can be found [here](https://github.com/users/Maxcode0101/projects/5). The MoSCoW method has been used to prioritize the project steps.

![KanbanBoard](documentation/readme/KanbanPP4.webp)

| Target | Expectation | Outcome |
| --- | --- | --- |
| As a prospective customer | I want to register for an account and log in | So that I can manage my bookings and receive notifications. |
| As a customer | I want to view a list of available campervans and filter them by brand, model, capacity, price, and availability dates | So that I can easily find a vehicle that meets my needs. |
| As a customer | I want to select a campervan and book it for a specific date range (with a minimum of 4 days from today) | So that I can reserve the vehicle for my trip. |
| As a customer | I want to view all my bookings in a dashboard | So that I can track their status (Pending, Confirmed, Ongoing, Past) and manage them. |
| As a customer | I want to update the dates for my pending booking via self-service | So that I can adjust my reservation if needed before payment. |
| As a customer | I want to request a date change for a confirmed booking | So that I can propose changes that require admin approval. |
| As a customer | I want to cancel a booking (only if it’s pending and in the future) | So that I can change my plans if necessary. |
| As an admin | I want to review and manage cancellation and date change requests | So that I can approve or reject them according to business rules. |
| As a user | I want a visually appealing and responsive website | So that my experience is seamless whether on mobile or desktop. |
| As a business owner | I want that reservations that are not getting paid by the customer within 3 days are automatically getting cancelled | so that the admin or staff doesn't have to manually cancel the unpaid reservations. |
| As a customer | I want to read customer reviews of past guests | so that I can have an impression of the quality of the offered campervans and service. |

## Features

### Existing Features

| Feature | Notes | Screenshot |
| --- | --- | --- |
| Register | Authentication is handled by allauth, allowing users to register accounts. | ![screenshot](documentation/readme/features/register.png) |
| Login | Authentication is handled by allauth, allowing users to log in to their existing accounts. | ![screenshot](documentation/readme/features/login.png) |
| Logout | Authentication is handled by allauth, allowing users to log out of their accounts. | ![screenshot](documentation/readme/features/logout.png) |
| About Us | The homepage displays basic information about the companies aim, including a hero image, title, and link to the contact page. | ![screenshot](documentation/readme/features/about_us.png) |
| FAQ's | Users can view frequently asked Questions and answers to it. | ![screenshot](documentation/readme/features/faq.png) |
| Contact Page | The Contact page displays the emailadresse and phone number of the service team, along with the option for visitors to fill out a contact form. | ![screenshot](documentation/readme/features/contact.png) |
| Our Campervans Page | The Our Campervans page displays pictures and descriptions of all our vehicles, along with the option for visitors use different filters to browse through them and check if they're available. | ![screenshot](documentation/readme/features/campervans.png) |
| Pagination | The campervan list is displayed in pages, with six vehicles per page. This provides better navigation for users through the campervan list. | ![screenshot](documentation/readme/features/pagination.png) |
| Dashboard | Authenticated visitors can see their upcoming and past bookings and see a link to the "My Bookings" section. | ![screenshot](documentation/readme/features/dashboard.png) |
| My Bookings Page | Authenticated visitors can watch details about, manage, update and cancel their bookings. Pending bookings can be changed (dates) or canceled via self service, while confirmed (paid) bookings can be only changed or canceled via admin aproval | ![screenshot](documentation/readme/features/my_bookings.png) |
| Checkout Page | Authenticated visitors can pay for their reservations in order to have a confirmed booking. | ![screenshot](documentation/readme/features/checkout.png) |
| Profile Page | Authenticated visitors can view their profile details (Username and Emailaddress). | ![screenshot](documentation/readme/features/profile.png) |
| Heroku Deployment | The site is fully deployed to Heroku, making it accessible online and easy to manage. | ![screenshot](documentation/readme/features/heroku.png) |
| 404 | The 404 error page will indicate when a user has navigated to a page that doesn't exist, replacing the default Heroku 404 page with one that ties into the site's look and feel. | ![screenshot](documentation/readme/features/404.png) |

### Future Features

- **Enhanced user profile page**: Further user data for profile page (like birthdate, and issuing date of drivers license)

- **Review section**: Guest can leave reviews, which are getting displayed in an exclusive section

- **Automated cancel reservation logic**: Automated flow which is deleting unpaid bookings after 3 days (72 hours) after the reservation had been made (Celery).

- **Campervan sharing plattform**: Giving other campervan owners the possibility to host their campervans on the site to make profit (a service charge per booking will apply)

- **Email Subscriptions**: Allow users to subscribe to receive email notifications for new campervans beeing added, updates to rental terms, sharing routes and other travel infos or newsletters.

- **SEO Optimization**: Implement features for SEO, such as meta tags, custom URLs, and keywords for better search engine ranking.

- **Admin Dashboard Analytics**: Provide site admins with an analytics dashboard showing user activity, most clicked campervans etc.


## Tools & Technologies

| Tool / Tech | Use |
| --- | --- |
| [![badge](https://img.shields.io/badge/Markdown_Builder-grey?logo=markdown&logoColor=000000)](https://markdown.2bn.dev) | Generate README and TESTING templates. |
| [![badge](https://img.shields.io/badge/Git-grey?logo=git&logoColor=F05032)](https://git-scm.com) | Version control. (`git add`, `git commit`, `git push`) |
| [![badge](https://img.shields.io/badge/GitHub-grey?logo=github&logoColor=181717)](https://github.com) | Secure online code storage. |
| [![badge](https://img.shields.io/badge/Gitpod-grey?logo=gitpod&logoColor=FFAE33)](https://gitpod.io) | Cloud-based IDE for development. |
| [![badge](https://img.shields.io/badge/VSCode-grey?logo=htmx&logoColor=007ACC)](https://code.visualstudio.com) | Local IDE for development. |
| [![badge](https://img.shields.io/badge/HTML-grey?logo=html5&logoColor=E34F26)](https://en.wikipedia.org/wiki/HTML) | Main site content and layout. |
| [![badge](https://img.shields.io/badge/CSS-grey?logo=css3&logoColor=1572B6)](https://en.wikipedia.org/wiki/CSS) | Design and layout. |
| [![badge](https://img.shields.io/badge/JavaScript-grey?logo=javascript&logoColor=F7DF1E)](https://www.javascript.com) | User interaction on the site. |
| [![badge](https://img.shields.io/badge/Python-grey?logo=python&logoColor=3776AB)](https://www.python.org) | Back-end programming language. |
| [![badge](https://img.shields.io/badge/Heroku-grey?logo=heroku&logoColor=430098)](https://www.heroku.com) | Hosting the deployed back-end site. |
| [![badge](https://img.shields.io/badge/Bootstrap-grey?logo=bootstrap&logoColor=7952B3)](https://getbootstrap.com) | Front-end CSS framework for modern responsiveness and pre-built components. |
| [![badge](https://img.shields.io/badge/Django-grey?logo=django&logoColor=092E20)](https://www.djangoproject.com) | Python framework for the site. |
| [![badge](https://img.shields.io/badge/PostgreSQL-grey?logo=postgresql&logoColor=4169E1)](https://www.postgresql.org) | Relational database management. |
| [![badge](https://img.shields.io/badge/Cloudinary-grey?logo=cloudinary&logoColor=3448C5)](https://cloudinary.com) | Online static file storage. |
| [![badge](https://img.shields.io/badge/WhiteNoise-grey?logo=python&logoColor=FFFFFF)](https://whitenoise.readthedocs.io) | Serving static files with Heroku. |
| [![badge](https://img.shields.io/badge/Font_Awesome-grey?logo=fontawesome&logoColor=528DD7)](https://fontawesome.com) | Icons. |
| [![badge](https://img.shields.io/badge/ChatGPT-grey?logo=openai&logoColor=75A99C)](https://chat.openai.com) | Help debug, troubleshoot, and explain things. |

## Database Design

### Data Model

#### Entity relationship diagram

This diagram shows how the users and staff users interact with the database.

![screenshot](documentation/readme/ERD%20Wildventures%20Django%20Project.png)

I have used Lucidchart to create an ERD.
- [Lucidchart](https://www.lucidchart.com

## Agile Development Process

### GitHub Projects

[GitHub Projects](https://www.github.com/Maxcode0101/campervan_rental/projects) served as an Agile tool for this project. Through it, EPICs, User Stories, issues/bugs, and Milestone tasks were planned, then subsequently tracked on a regular basis using the Kanban project board.

![screenshot](documentation/readme/KanbanPP4.webp)

### GitHub Issues

[GitHub Issues](https://www.github.com/Maxcode0101/campervan_rental/issues) served as an another Agile tool. There, I managed my User Stories and Milestone tasks, and tracked any issues/bugs.

| Link | Screenshot |
| --- | --- |
| [![GitHub issues](https://img.shields.io/github/issues/Maxcode0101/campervan_rental)](https://www.github.com/Maxcode0101/campervan_rental/issues) | ![screenshot](documentation/readme/gh-issues-open.png) |
| [![GitHub closed issues](https://img.shields.io/github/issues-closed/Maxcode0101/campervan_rental)](https://www.github.com/Maxcode0101/campervan_rental/issues?q=is%3Aissue+is%3Aclosed) | ![screenshot](documentation/readme/gh-issues-closed.png) |

### MoSCoW Prioritization

I've decomposed my Epics into User Stories for prioritizing and implementing them. Using this approach, I was able to apply "MoSCow" prioritization and labels to my User Stories within the Issues tab.

- **Must Have**: guaranteed to be delivered - required to Pass the project (*max ~60% of stories*)
- **Should Have**: adds significant value, but not vital (*~20% of stories*)
- **Could Have**: has small impact if left out (*the rest ~20% of stories*)
- **Won't Have**: not a priority for this iteration - future features

## Testing

> [!NOTE]
> For all testing, please refer to the [TESTING.md](TESTING.md) file.

## Deployment

The live deployed application can be found deployed on [Heroku](https://campervan-rental-923a0b226ad3.herokuapp.com).

### Heroku Deployment

This project uses [Heroku](https://www.heroku.com), a platform as a service (PaaS) that enables developers to build, run, and operate applications entirely in the cloud.

Deployment steps are as follows, after account setup:

- Select **New** in the top-right corner of your Heroku Dashboard, and select **Create new app** from the dropdown menu.
- Your app name must be unique, and then choose a region closest to you (EU or USA), then finally, click **Create App**.
- From the new app **Settings**, click **Reveal Config Vars**, and set your environment variables to match your private `env.py` file.

> [!IMPORTANT]
> This is a sample only; you would replace the values with your own if cloning/forking my repository.

| Key | Value |
| --- | --- |
| `CLOUDINARY_URL` | user-inserts-own-cloudinary-url |
| `DATABASE_URL` | user-inserts-own-postgres-database-url |
| `DISABLE_COLLECTSTATIC` | 1 (*this is temporary, and can be removed for the final deployment*) |
| `SECRET_KEY` | any-random-secret-key |

Heroku needs some additional files in order to deploy properly.

- [requirements.txt](requirements.txt)
- [Procfile](Procfile)

You can install this project's **[requirements.txt](requirements.txt)** (*where applicable*) using:

- `pip3 install -r requirements.txt`

If you have your own packages that have been installed, then the requirements file needs updated using:

- `pip3 freeze --local > requirements.txt`

The **[Procfile](Procfile)** can be created with the following command:

- `echo web: gunicorn app_name.wsgi > Procfile`
- *replace `app_name` with the name of your primary Django app name; the folder where `settings.py` is located*

For Heroku deployment, follow these steps to connect your own GitHub repository to the newly created app:

Either (*recommended*):

- Select **Automatic Deployment** from the Heroku app.

Or:

- In the Terminal/CLI, connect to Heroku using this command: `heroku login -i`
- Set the remote for Heroku: `heroku git:remote -a app_name` (*replace `app_name` with your app name*)
- After performing the standard Git `add`, `commit`, and `push` to GitHub, you can now type:
	- `git push heroku main`

The project should now be connected and deployed to Heroku!

### Cloudinary API

This project uses the [Cloudinary API](https://cloudinary.com) to store media assets online, due to the fact that Heroku doesn't persist this type of data.

To obtain your own Cloudinary API key, create an account and log in.

- For "Primary Interest", you can choose **Programmable Media for image and video API**.
- *Optional*: edit your assigned cloud name to something more memorable.
- On your Cloudinary Dashboard, you can copy your **API Environment Variable**.
- Be sure to remove the leading `CLOUDINARY_URL=` as part of the API **value**; this is the **key**.
    - `cloudinary://123456789012345:AbCdEfGhIjKlMnOpQrStuVwXyZa@1a2b3c4d5)`
- This will go into your own `env.py` file, and Heroku Config Vars, using the **key** of `CLOUDINARY_URL`.

### PostgreSQL

This project uses a [Code Institute PostgreSQL Database](https://dbs.ci-dbs.net) for the Relational Database with Django.

> [!CAUTION]
> - PostgreSQL databases by Code Institute are only available to CI Students.
> - You must acquire your own PostgreSQL database through some other method if you plan to clone/fork this repository.
> - Code Institute students are allowed a maximum of 8 databases.
> - Databases are subject to deletion after 18 months.

To obtain my own Postgres Database from Code Institute, I followed these steps:

- Submitted my email address to the CI PostgreSQL Database link above.
- An email was sent to me with my new Postgres Database.
- The Database connection string will resemble something like this:
    - `postgres://<db_username>:<db_password>@<db_host_url>/<db_name>`
- You can use the above URL with Django; simply paste it into your `env.py` file and Heroku Config Vars as `DATABASE_URL`.

### WhiteNoise

This project uses the [WhiteNoise](https://whitenoise.readthedocs.io/en/latest/) to aid with static files temporarily hosted on the live Heroku site.

To include WhiteNoise in your own projects:

- Install the latest WhiteNoise package:
    - `pip install whitenoise`
- Update the `requirements.txt` file with the newly installed package:
    - `pip freeze --local > requirements.txt`
- Edit your `settings.py` file and add WhiteNoise to the `MIDDLEWARE` list, above all other middleware (apart from Django’s "SecurityMiddleware"):

```python
# settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # any additional middleware
]
```


### Local Development

This project can be cloned or forked in order to make a local copy on your own system.

For either method, you will need to install any applicable packages found within the [requirements.txt](requirements.txt) file.

- `pip3 install -r requirements.txt`.

You will need to create a new file called `env.py` at the root-level, and include the same environment variables listed above from the Heroku deployment steps.

> [!IMPORTANT]
> This is a sample only; you would replace the values with your own if cloning/forking my repository.

Sample `env.py` file:

```python
import os

os.environ.setdefault("SECRET_KEY", "any-random-secret-key")
os.environ.setdefault("DATABASE_URL", "user-inserts-own-postgres-database-url")
os.environ.setdefault("CLOUDINARY_URL", "user-inserts-own-cloudinary-url")  # only if using Cloudinary

# local environment only (do not include these in production/deployment!)
os.environ.setdefault("DEBUG", "True")
```

Once the project is cloned or forked, in order to run it locally, you'll need to follow these steps:

- Start the Django app: `python3 manage.py runserver`
- Stop the app once it's loaded: `CTRL+C` (*Windows/Linux*) or `⌘+C` (*Mac*)
- Make any necessary migrations: `python3 manage.py makemigrations --dry-run` then `python3 manage.py makemigrations`
- Migrate the data to the database: `python3 manage.py migrate --plan` then `python3 manage.py migrate`
- Create a superuser: `python3 manage.py createsuperuser`
- Load fixtures (*if applicable*): `python3 manage.py loaddata file-name.json` (*repeat for each file*)
- Everything should be ready now, so run the Django app again: `python3 manage.py runserver`

If you'd like to backup your database models, use the following command for each model you'd like to create a fixture for:

- `python3 manage.py dumpdata your-model > your-model.json`
- *repeat this action for each model you wish to backup*
- **NOTE**: You should never make a backup of the default *admin* or *users* data with confidential information.

#### Cloning

You can clone the repository by following these steps:

1. Go to the [GitHub repository](https://www.github.com/Maxcode0101/campervan_rental).
2. Locate and click on the green "Code" button at the very top, above the commits and files.
3. Select whether you prefer to clone using "HTTPS", "SSH", or "GitHub CLI", and click the "copy" button to copy the URL to your clipboard.
4. Open "Git Bash" or "Terminal".
5. Change the current working directory to the location where you want the cloned directory.
6. In your IDE Terminal, type the following command to clone the repository:
	- `git clone https://www.github.com/Maxcode0101/campervan_rental.git`
7. Press "Enter" to create your local clone.

Alternatively, if using Gitpod, you can click below to create your own workspace using this repository.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://www.github.com/Maxcode0101/campervan_rental)

**Please Note**: in order to directly open the project in Gitpod, you should have the browser extension installed. A tutorial on how to do that can be found [here](https://www.gitpod.io/docs/configure/user-settings/browser-extension).

#### Forking

By forking the GitHub Repository, you make a copy of the original repository on our GitHub account to view and/or make changes without affecting the original owner's repository. You can fork this repository by using the following steps:

1. Log in to GitHub and locate the [GitHub Repository](https://www.github.com/Maxcode0101/campervan_rental).
2. At the top of the Repository, just below the "Settings" button on the menu, locate and click the "Fork" Button.
3. Once clicked, you should now have a copy of the original repository in your own GitHub account!

### Local VS Deployment

There are no remaining major differences between the local version when compared to the deployed version online.

## Credits

### Content

| Source | Notes |
| --- | --- |
| [Markdown Builder](https://markdown.2bn.dev) | Help generating Markdown files |
| [Chris Beams](https://chris.beams.io/posts/git-commit) | "How to Write a Git Commit Message" |
| [I Think Therefore I Blog](https://codeinstitute.net) | Code Institute walkthrough project inspiration |
| [Bootstrap](https://getbootstrap.com) | Various components / responsive front-end framework |
| [Cloudinary API](https://cloudinary.com) | Cloud storage for static/media files |
| [Whitenoise](https://whitenoise.readthedocs.io) | Static file service |
| [ChatGPT](https://chatgpt.com) | Help with code logic and explanations |

### Media

- Images
    - [I'm the owner, havig exclusive rights for some media files used in this      project] (Hero Image, Wildventures company logo, campervan pictures of: Overlander, Economist and Retro Camper)
    - [Pexels](https://www.pexels.com) -> Has been used to find the pictures for all the remaining campervans
    

| Source | Notes |
| --- | --- |
| [favicon.io](https://favicon.io) | Generating the favicon |
| [Font Awesome](https://fontawesome.com) | Icons used throughout the site |
| [Pexels](https://images.pexels.com/photos/416160/pexels-photo-416160.jpeg) | Hero image |
| [CloudConvert](https://cloudconvert.com/webp-converter) | Converting images to `.webp` |

### Acknowledgements

- I would like to thank my Code Institute mentor, [Tim Nelson](https://www.github.com/TravelTimN) for the support throughout the development of this project.
- I would like to thank the [Code Institute](https://codeinstitute.net) Tutor Team for their assistance with troubleshooting and debugging some project issues.
- I would like to thank the [Code Institute Slack community](https://code-institute-room.slack.com) for the moral support; it kept me going during periods of self doubt and impostor syndrome.