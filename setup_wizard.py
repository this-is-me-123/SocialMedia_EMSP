import os
from getpass import getpass

FIELDS = [
    ("POSTGRES_DB", "Database name", "socialmedia"),
    ("POSTGRES_USER", "Database user", "socialmedia"),
    ("POSTGRES_PASSWORD", "Database password", None),
    ("JWT_SECRET_KEY", "JWT secret key", None),
    ("CORS_ALLOW_ORIGINS", "Allowed CORS origins (comma-separated)", "http://localhost:5173"),
    ("INSTAGRAM_CLIENT_ID", "Instagram client ID", None),
    ("INSTAGRAM_CLIENT_SECRET", "Instagram client secret", None),
    ("TIKTOK_CLIENT_KEY", "TikTok client key", None),
    ("TIKTOK_CLIENT_SECRET", "TikTok client secret", None),
    ("INSTAGRAM_VERIFY_TOKEN", "Instagram webhook verify token", None),
]

def prompt():
    print("\n--- SocialMedia_EMSP Preinstall Setup Wizard ---\n")
    env_lines = []
    for key, desc, default in FIELDS:
        if default is not None:
            prompt_str = f"{desc} [{default}]: "
        else:
            prompt_str = f"{desc}: "
        if 'PASSWORD' in key or 'SECRET' in key:
            val = getpass(prompt_str)
        else:
            val = input(prompt_str)
        if not val and default is not None:
            val = default
        env_lines.append(f"{key}={val}")
    env_content = "\n".join(env_lines)
    with open(".env", "w") as f:
        f.write(env_content + "\n")
    print("\n.env file created. You can now run: docker-compose up --build -d\n")

if __name__ == "__main__":
    prompt()
