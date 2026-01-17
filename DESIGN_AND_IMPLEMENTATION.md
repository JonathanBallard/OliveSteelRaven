
# Design & Implementation Plan

## Planning Phases

- Database Schema
  - ERD Diagram
  - Created in Workbench
- Readme
  - Be sure to include additional software and tools to try out
- License
- Learning Goals
- Plan of Action
  - Decide on a progress tracking method
    - Track time usage on items

### Plan your project in advance

Goal is to have a clearly defined plan that can be executed on and will still leave information for a retrospective after project completion.  
Ideally the plan will be repeatable and refinable for future projects.

- Do research on how people plan software projects
- Choose tech stack
- Build out monday.com task list and plans
- Build out clearly defined workflow
- [Video 1](https://youtu.be/AGWyx96lP8U)
- [Video 2](https://www.youtube.com/watch?v=GjLxI1yTWoY)
- [Video 3](https://www.youtube.com/watch?v=WR1ydijTx5E&pp=ugUHEgVlbi1VUw%3D%3D)
- [Link 1](https://www.usemotion.com/blog/software-project-planning)

### Workflow so far

1. *DONE* Research your project
2. *DONE* Choose your tech stack
3. *DONE* Use DrawSQL.org to create your ERD and Database Schema
4. *DONE* Create a README with outline of project, tools to use, and plans
5. *DONE* Create a license file with a license
6. *DONE* Create the Project folder and attach to a Github Repo
7. *DONE* Create a list of tasks on Monday.com
8. *DONE* Create wireframes/mockups on Framer
9. *DONE* Create Design elements (background image, logo, etc...) on Canva
10. *DONE* Create batch files for development servers
11. Create typography/font sizes
12. Create color palettes
13. *DONE* Create Django project and Django App(s)
14. *DONE* Setup Database to work with Django
15. *DONE* Creating Views in Django
16. *DONE* Plan models based on Django Apps
17. Create `accounts` views.py
18. Create `recipes` views.py

### Fonts & Sizes

Title: Libre Baskerville
Body: Roboto 18pt
Others: Archivo

### Color Palettes

Palette 1

- #91B2CF
- #A9CD87
- #C1CDA3
- #E4C99F
- #A57772

Palette 2

- #91B2CF
- #A9CD87
- #F6D42A
- #D87725
- #DC3743

### Project Organization

#### Pages

Home
Login
Signup
Browse Categories -> Each category simply runs a search for that 'type'
Search Recipes
Search Results
Recipe Details
Account
Show my Recipes -> Runs a search with all recipes you've created

#### Locations

- Project Wide Utilities are stored in OliveSteelRaven/osr/common/utils.py
- App-specific utils.py exist as well
- Templates are stored in each app in this way: OliveSteelReaven/osr/app_name/templates/app_name/my_template.html
- Each app contains it's own models.py
- Each app contains it's own views.py
- Each app contains it's own urls.py
- The Project Wide urls.py imports from the apps urls.py

#### Apps

1. Accounts - Contains all user authentication and validation logic
2. Recipes - Contains CRUD for Recipes
3. Comments - If implemented, will contain logic for commenting on recipes
4. Ratings - Ifi implemented, will contain logic for rating recipes

#### Database

##### Users Table

id - bigint
username - mediumtext
email - mediumtext
password - longtext
image - blob
recipes_authored - foreign key (recipes junction table)
recipes_favorited - foreign key (recipes junction table)
recipes_attempted - foreign key (recipes junction table)
recipe_rating - foreign key (recipes junction table)
created_at - datetime
last_login - datetime

##### Recipes Table

id - bigint
title - mediumtext
tags - longtext
description_short - mediumtext
description_long - longtext
difficulty - smallint
user_rating - smallint
preparation_time 0 text
allergies - text (DELETE?)
ingredients - json
instructions - json
views - bigint
attempts - bigint
created_by - foreign key (users)
created_at - datetime
updated_at - datetime

### Considerations

#### Additional Tools and Technologies Considered

1. React - For reusable components. Primarily would be used for cards, nav, footer, and search results
2. JWT - For authentication and security
3. Auth0 - For login/signup simplicity
4. dotenv - For handling secrets (Implemented)
5. [Render](https://render.com/docs/deploy-django) - To deploy Backend on and keep Framer Front-End
6. [PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/) - Same as Render
7. Tailwind CSS - Instead of Bootstrap

#### Things to Consider Doing Differently

1. Use Django's Forms and Templates
