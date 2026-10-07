# A Beginner's Guide to Docker (for Data Engineering)

Welcome to Docker! Docker is a tool that allows you to package and run applications in isolated environments called **containers**. 

Think of a container like a lightweight, temporary virtual machine. Instead of installing PostgreSQL directly on your computer (which can be messy and hard to uninstall), you tell Docker: *"Hey, download the official PostgreSQL image and run it for me."*

For this project, we are using **Docker Compose**, which is a feature of Docker that lets you define and run multi-container applications using a simple YAML file (`docker-compose.yml`).

## 1. What is `docker-compose.yml`?
If you look at the `docker-compose.yml` file in this project, you'll see we defined a service called `postgres`. 
- **image:** `postgres:15` tells Docker to use the official PostgreSQL version 15.
- **environment:** Sets up our default username, password, and database name.
- **ports:** `"5432:5432"` connects your computer's port 5432 to the container's port 5432. This means you can connect to the database from Python exactly as if it were installed directly on your machine.
- **volumes:** `pgdata:/var/lib/postgresql/data` ensures that even if you destroy the container, your database data is saved safely on your hard drive.

## 2. Essential Docker Commands

Open your terminal in this project's directory and try these commands:

### Start your database
```bash
docker compose up -d
```
- `up` means "start the containers".
- `-d` means "detached mode" (runs in the background so you can keep using your terminal).

### Check if it's running
```bash
docker ps
```
This lists all active containers. You should see `wwi-postgres` in the list with a status of "Up".

### View database logs
If you ever want to see what the database is doing behind the scenes:
```bash
docker compose logs -f
```
- `-f` means "follow" (streams the logs live). Press `Ctrl+C` to exit.

### Stop the database
When you're done working for the day:
```bash
docker compose stop
```
This stops the container but keeps it around for next time.

### Completely remove the database (Reset)
If you mess up your database and want a completely fresh start:
```bash
docker compose down -v
```
- `down` stops and removes the container.
- `-v` deletes the saved data volume (meaning **all data will be lost**!). Only do this if you want to wipe the slate clean.

## 3. Next Steps
Now that you know the basics, try running `docker compose up -d` in your terminal to start your PostgreSQL database! Once it's running, we can proceed with loading the raw CSV data into it.
