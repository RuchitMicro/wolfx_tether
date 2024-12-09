# ✨ Tether - Web-Based SSH Access Right in Your Browser

Tether is a solution for deployment engineers, site reliability engineers, and infrastructure teams who need secure, browser-based SSH access without fuss. Instead of wrestling with local terminal configurations or cumbersome SSH keys, Tether lets you launch secure sessions directly from your browser. Just point, click, and get to work—wherever you are, on any device.


## 🚀 What is Tether?

Imagine you’re on the go, or maybe using a device without a terminal at hand. Tether lets you jump into a secure SSH session straight from your web browser. It leverages Django and Channels to provide real-time, bi-directional communication with remote hosts—like a browser-based terminal on steroids! 
Tether transforms your browser into a dynamic SSH terminal, eliminating the need for a local shell or complicated SSH setups. It leverages Django and Channels to deliver responsive, real-time connections to remote hosts. With Tether, you’re always just one click away from a fully interactive session—no extra software required.


## 💡 Why Tether is created?

Too often, secure credentials get shared too liberally, slipping through Slack messages or emails. Tether changes the game by centralizing and locking down the authentication process. Administrators assign authorized access inside Tether’s admin dashboard, ensuring that only the right people can connect to the right servers. This cuts down on risky credential sharing, bolsters your security posture, and keeps your infrastructure safe from unauthorized access.


## 🛠️ How It Works

- **Admin Setup**: Tether’s admin interface (found at http://localhost/admin) makes it simple to add new servers. Fill in the host’s details—name, IP, port, username, password, PEM file, and a descriptive note—and assign permissions to the specific users who need access.
- **User Login**: Once logged into http://localhost, users see a curated list of servers they’re allowed to connect to. From there, it’s a single click on “Connect” to launch a fully functional SSH session right in the browser window.
- **Seamless Disconnect**: A built-in kill switch ensures that ending a session is as easy and reliable as starting one. No loose ends, no lingering connections—just clean, secure shutdowns.


## 🔒 Security First

From day one, Tether is engineered with security as a top priority. Strict object-level permissions ensure that users only see the hosts they’re cleared to access. This approach prevents accidental or malicious breaches, guaranteeing that each server connection is both authorized and auditable.


## 🎯 Key Features

- **Browser-Based SSH**: Connect to your servers directly from your browser—no external tools needed.
- **Object-Level Permissions**: Restrict access to only those hosts that users are authorized to view.
- **Interactive Terminal**: Enjoy full keyboard interactivity, scrollback buffers, and a responsive interface.
- **User-Friendly UI**: A clean, modern interface keeps the focus on what matters: managing your servers.


## Start the web app: 
gunicorn --bind 0.0.0.0:8000 web.wsgi:application


## Start the websocket: 
uvicorn wolfx_tether.asgi:application --port 8080


## Future Plan
- **Activity Logging and Auditing**: A forthcoming enhancement will let you log user commands and connection details, ensuring greater oversight and compliance.
