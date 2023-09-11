# htmx-fastapi

This is a demonstation on how to use HTMX and FasAPI together.

After cloning this Repo:

```properties
git clone https://github.com/devaxio/htmx-fastapi/
```

Open that directory, and then use `conda` to create and activate an enviroment:

```properties
conda create --name <env> --file requirments.txt
conda activate <env>
```
* Change `<env>` with any name you want.

Then, run the `uvicorn` server:
```properties
uvicorn htmx-fastapi:app --reload
```
