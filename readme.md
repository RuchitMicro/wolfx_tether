# ✨ Tether - Web-Based SSH Access Right in Your Browser

Tether is a web-based SSH solution that empowers deployment engineers, site reliability engineers, and infrastructure teams to securely connect to remote servers without leaving the browser environment. With Tether, you don’t need a local terminal or complicated SSH setup—just click, connect, and get to work!

## 🚀 What is Tether?

Imagine you’re on the go, or maybe using a device without a terminal at hand. Tether lets you jump into a secure SSH session straight from your web browser. It leverages Django and Channels to provide real-time, bi-directional communication with remote hosts—like a browser-based terminal on steroids! Tether was created to discourage ssh owners to share important credentials directly with each other. Instead the permitted user can directly login to tether and they are provided with options to connect to the server directly.

## 🔒 Security First

Tether enforces strict object-level permissions so only authorized users can view and connect to specific hosts. This ensures that no one can access servers they’re not supposed to, safeguarding your infrastructure’s integrity.

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
- **Add Activity Logger**: Log commands and user activity on a server after the login
