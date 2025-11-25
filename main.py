import requests

# ===== CONFIGURATION =====
USERNAME = "#"  # Replace with your GitHub username
TOKEN = "#"  # Must have 'delete_repo' and 'repo' permissions

# ===== FETCH PUBLIC REPOSITORIES =====
url = "https://api.github.com/user/repos?per_page=100&type=public"
headers = {"Authorization": f"token {TOKEN}"}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print("Failed to fetch repositories. Check your token or network.")
    print(f"Response: {response.status_code} - {response.text}")
    exit()

repos = response.json()

# ===== DISPLAY & DELETE PUBLIC REPOS =====
if not repos:
    print("No public repositories found.")
else:
    print(f"Found {len(repos)} public repositories:\n")

    for repo in repos:
        name = repo["name"]
        print(f"Repository: {name}")

        confirm = input(
            f"Do you want to delete the public repository '{name}'? (y/n): "
        ).strip().lower()
        if confirm == "y":
            del_url = f"https://api.github.com/repos/{USERNAME}/{name}"
            del_response = requests.delete(del_url, headers=headers)

            if del_response.status_code == 204:
                print(f"Deleted: {name}\n")
            else:
                print(
                    f"Failed to delete {name}. Status: {del_response.status_code} | {del_response.text}\n"
                )
        else:
            print(f"Skipped: {name}\n")

print("Finished checking all public repositories.")
