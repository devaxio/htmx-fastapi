# Import necessary modules and classes from FastAPI and SQLAlchemy
from fastapi import FastAPI, Request, Response          # to create the app and routes
from fastapi.templating import Jinja2Templates          # to access and process templates
from fastapi.staticfiles import StaticFiles             # self-explanatory
from fastapi.responses import HTMLResponse              # to respond with HTML instead of JSON
from sqlalchemy import create_engine, Column,\
    Integer, String, Boolean                            # to create the database
from sqlalchemy.orm import sessionmaker                 # to access the database
from sqlalchemy.ext.declarative import declarative_base # to implicitly define the database structure.
from pathlib import Path                                # to specify the static assets' directory
import urllib.parse                                     # to parse URL encoded data

# Create a FastAPI application instance
app = FastAPI()

# Mount a static files directory to serve static assets
# (e.g., CSS, and JS libs for htmx and hyperscript)
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

# Set up a database engine to connect to an SQLite database file
engine = create_engine("sqlite:///./todolist.db")

# Create a base class for declarative ORM models
Base = declarative_base()

# Define SQLAlchemy models for
## Personal tasks
class PersonalTask(Base):
    __tablename__ = "personal_tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(Boolean)

## Work tasks
class WorkTask(Base):
    __tablename__ = "work_tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(Boolean)

## Shopping tasks
class ShoppingTask(Base):
    __tablename__ = "shopping_tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(Boolean)

# Create the database tables based on the defined models
Base.metadata.create_all(engine)

# Create a session maker to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Set up Jinja2 templates for rendering HTML pages
templates = Jinja2Templates(directory="templates")

#######################
#######################
## Define app routes ##
#######################
#######################

##################################
# Route for the home page (root) #
##################################
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Render the "index.html" template with the given request
    return templates.TemplateResponse("index.html", {"request": request})

####################################
# Define routes for personal tasks #
####################################

# Route to display all personal tasks
@app.get("/tasks/personal", response_class=HTMLResponse)
async def get_personal_tasks(request: Request):
    # Query the database to retrieve all personal tasks
    tasks = session.query(PersonalTask).all()
    # Render the "tasks.html" template with the list of tasks and category set to "personal"
    # The rest of categories will have category set to their name
    # It'll help in the templates to add endpoints to each interactive component
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "category":"personal"})

# Route to create a new personal task
@app.post("/tasks/personal", response_class=HTMLResponse)
async def create_personal_task(request: Request):
    # Retrieve the task name from the request body
    body = await request.body()
    # Decode the name as it'll be URL encoded
    name = urllib.parse.unquote(body.decode().split("=")[1])
    # Set the initial status of the task to False, denoting incompletion
    status = False
    # Create a new PersonalTask object with the provided name and status
    personal_task = PersonalTask(name=name, status=status)
    # Add the task to the database and commit the changes
    session.add(personal_task)
    session.commit()
    # Retrieve all personal tasks and render the "tasks.html" template
    # To update the table of tasks on the go
    tasks = session.query(PersonalTask).all()
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "category":"personal"})

# Route to update the status of a personal task
@app.put("/tasks/personal/{task_id}", response_class=HTMLResponse)
async def update_personal_task(task_id: int, request: Request):
    # Query the database to find the personal task by its ID
    personal_task = session.query(PersonalTask).filter(PersonalTask.id == task_id).first()

    if personal_task is None:
        # If the task is not found, raise an HTTPException with a 404 status
        raise HTTPException(status_code=404, detail="Personal task not found")

    # Toggle the status of the personal task (from True to False or vice versa)
    personal_task.status = not personal_task.status
    # Commit the changes to the database
    session.commit()
    # Render the "task.html" template with the updated task and category set to "personal"
    # To only update the toggled task without updating the whole DOM
    return templates.TemplateResponse("task.html", {"request": request, "task": personal_task, "category":"personal"})

# Route to display a confirmation modal before deleting a personal task
@app.get("/tasks/personal/confirm-delete/{task_id}", response_class=HTMLResponse)
async def get_personal_task_delete_confirmation(task_id: int, request: Request):
    # Query the database to find the personal task by its ID
    personal_task = session.query(PersonalTask).filter(PersonalTask.id == task_id).first()
    if personal_task is None:
        # If the task is not found, raise an HTTPException with a 404 status
        raise HTTPException(status_code=404, detail="You can't delete a non-existing task")
    tasks = session.query(PersonalTask).all()
    # Render the confirmation modal for the specific task deletion
    return templates.TemplateResponse("modal.html", {"request":request,"tasks": tasks, "task":personal_task, "category":"personal" })

# Route to delete a personal task
@app.delete("/tasks/personal/{task_id}", response_class=HTMLResponse)
async def delete_personal_task(task_id: int, request: Request):
    # Query the database to find the personal task by its ID
    personal_task = session.query(PersonalTask).filter(PersonalTask.id == task_id).first()
    if personal_task is None:
        # If the task is not found, raise an HTTPException with a 404 status
        raise HTTPException(status_code=404, detail="You can't delete a non-existing task")
    # Delete the personal task from the database and commit the changes
    session.delete(personal_task)
    session.commit()
    # We are returning None so we can swap it (meaning delete) the single task from the DOM
    # in case we are deleting the last task, we'll update the content and remove the table
    # so we are better reflecting what is on the database
    tasks = session.query(PersonalTask).all()
    if len(tasks) != 0:
        return None
    else:
        return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "category":"personal"})

################################
# Define routes for work tasks #
################################

@app.get("/tasks/work", response_class=HTMLResponse)
async def get_work_tasks(request: Request):
    tasks = session.query(WorkTask).all()
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "category":"work"})

@app.post("/tasks/work", response_class=HTMLResponse)
async def create_work_task(request: Request):
    body = await request.body()
    name = urllib.parse.unquote(body.decode().split("=")[1])
    status = False
    work_task = WorkTask(name=name, status=status)
    session.add(work_task)
    session.commit()
    tasks = session.query(WorkTask).all()
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "category":"work"})

@app.put("/tasks/work/{task_id}", response_class=HTMLResponse)
async def update_work_task(task_id: int, request: Request):
    work_task = session.query(WorkTask).filter(WorkTask.id == task_id).first()
    if work_task is None:
        raise HTTPException(status_code=404, detail="Work task not found")
    work_task.status = not work_task.status
    session.commit()
    return templates.TemplateResponse("task.html", {"request": request, "task": work_task, "category":"work"})

@app.get("/tasks/work/confirm-delete/{task_id}", response_class=HTMLResponse)
async def get_work_task_delete_confirmation(task_id: int, request: Request):
    work_task = session.query(WorkTask).filter(WorkTask.id == task_id).first()
    if work_task is None:
        raise HTTPException(status_code=404, detail="You can't delete a non-existing work task!")
    tasks = session.query(WorkTask).all()
    return templates.TemplateResponse("modal.html", {"request":request, "tasks":tasks, "task":work_task, "category":"work" })

@app.delete("/tasks/work/{task_id}", response_class=HTMLResponse)
async def delete_work_task(task_id: int, request: Request):
    work_task = session.query(WorkTask).filter(WorkTask.id == task_id).first()
    if work_task is None:
        raise HTTPException(status_code=404, detail="You can't delete a non-existing work task!")
    session.delete(work_task)
    session.commit()
    tasks = session.query(WorkTask).all()
    if len(tasks) != 0:
        return None
    else:
        return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "category":"work"})

####################################
# Define routes for shopping tasks #
####################################

@app.get("/tasks/shopping", response_class=HTMLResponse)
async def get_shopping_tasks(request: Request):
    tasks = session.query(ShoppingTask).all()
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "category":"shopping"})

@app.post("/tasks/shopping", response_class=HTMLResponse)
async def create_shopping_task(request: Request):
    body = await request.body()
    name = urllib.parse.unquote(body.decode().split("=")[1])
    status = False
    shopping_task = ShoppingTask(name=name, status=status)
    session.add(shopping_task)
    session.commit()
    tasks = session.query(ShoppingTask).all()
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "category":"shopping"})

@app.put("/tasks/shopping/{task_id}", response_class=HTMLResponse)
async def update_shopping_task(task_id: int, request: Request):
    shopping_task = session.query(ShoppingTask).filter(ShoppingTask.id == task_id).first()
    if shopping_task is None:
        raise HTTPException(status_code=404, detail="Shopping task not found")
    shopping_task.status = not shopping_task.status
    session.commit()
    return templates.TemplateResponse("task.html", {"request": request, "task": shopping_task, "category":"shopping"})

@app.get("/tasks/shopping/confirm-delete/{task_id}", response_class=HTMLResponse)
async def get_shopping_task_delete_confirmation(task_id: int, request: Request):
    shopping_task = session.query(ShoppingTask).filter(ShoppingTask.id == task_id).first()
    if shopping_task is None:
        raise HTTPException(status_code=404, detail="You can't delete a non-existing shopping task!")
    tasks = session.query(ShoppingTask).all()
    return templates.TemplateResponse("modal.html", {"request":request, "tasks": tasks, "task":shopping_task, "category":"shopping" })

@app.delete("/tasks/shopping/{task_id}", response_class=HTMLResponse)
async def delete_shopping_task(task_id: int, request: Request):
    shopping_task = session.query(ShoppingTask).filter(ShoppingTask.id == task_id).first()
    if shopping_task is None:
        raise HTTPException(status_code=404, detail="You can't delete a non-existing shopping task!")
    session.delete(shopping_task)
    session.commit()
    tasks = session.query(ShoppingTask).all()
    if len(tasks) != 0:
        return None
    else:
        return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks, "category":"shopping"})