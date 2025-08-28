# 🔥 fuzzy-httpserver

A lightweight, zero-dependency Python HTTP file server with fuzzy filename matching and automatic fallback directory listing. Serve files easily without requiring users to know exact filenames — great for red teams, internal tooling, and lazy typing 😎.

---

## 🚀 Features

- 🔍 Fuzzy and prefix-based filename matching
- 🧾 Server-side logs directory contents if no file is matched
- ⚙️ Supports custom port and directory configuration
- ✅ No external dependencies — plug-and-play
- 🐍 Written in pure Python 3
- 📤 Supports POST data requests
- 🎨 Colored server-side output for better readability
- 🖵 Shows IP addresses of key network interfaces at startup
- Shows the Size and MD5 Hash of Received File - Integrity Check

### 🚀 Major Update 1.5.0

Now **Fuzzy-HTTPServer** can install a collection of essential binaries you’ll need during CTFs or pentest engagements, including:

* Custom exploit code in **C**
* All the *Potato* privilege escalation binaries (`.exe` and PowerShell)
* Privilege escalation enumeration scripts
* Essential PowerShell tooling (e.g., **SharpHound**)
* Pivoting agents, static builds of **netcat**, **nmap**, and more

In short: **almost every deliverable binary you might need — all in one place.**

🔜 More binaries will be added soon, along with a feature to **update specific binaries to their latest versions automatically.**

---

## 📦 Installation

Install via pip:

```bash
pip install fuzzy-httpserver
````

---

## 🧪 Usage

Serve the current directory on the default port (8000):

```bash
fuzzy-httpserver
```

Serve a specific directory on a custom port:

```bash
fuzzy-httpserver -d /opt/tools -p 9001
```
### 📥 Install Pre-Bundled Binaries

You can extract and install a curated collection of binaries needed for CTFs and pentests
(e.g., Potato exploits, privilege escalation scripts, SharpHound, pivoting agents, static netcat/nmap, etc.).

Simply specify an output directory with `-i`:

```bash
fuzzy-httpserver -i /opt/redteam-tools
```
⚠️ Note: You must have 7z installed.
If missing, run:
```
sudo apt install p7zip-full
```
### Example

```bash
wget http://<ip>:8000/ligolo-win
```

Even if the exact file is `ligolo-Agent-Windows-amd.exe`, it will still serve the file thanks to fuzzy matching. If nothing is found, you’ll get:

```
[!] File not found. Available files:

- chisel_windows
- payload_generator
```

Basically the list of files on that server directory

---

## 🛠 Command-Line Options

| Option              | Description                               |
| ------------------- | ----------------------------------------- |
| `-p`, `--port`      | Port to listen on (default: 8000)         |
| `-d`, `--directory` | Directory to serve (default: current dir) |
| `-i`, `--install`   | Install essential binaries (extracted from `transfers.7z`) into given path  |

## 📨 POST Support

You can now send raw data via HTTP POST, and it will be saved on the server as a file. The filename will be prefixed with `fuzzy_post_data_` followed by the requested name.

### Example

```bash
curl --data @file.txt http://<ip>:8000/mydump.txt
#OR
curl --data "username=admin&password=1234" http://<ip>:8000/formdata.txt
```

---

## 🧠 Why?

Sometimes during internal testing, CTFs, or red teaming, we just want to serve files quickly — but can’t remember exact filenames. `fuzzy-httpserver` saves time by letting you guess loosely.

---

## 🧑‍💻 Author & Credits

Built with 💻 and ☕ by [PakCyberbot](https://pakcyberbot.com).

🔗 Connect with me:

* 🌐 Website: http://pakcyberbot.com
* Twitter/x: https://x.com/pakcyberbot
* GitHub: https://github.com/PakCyberbot
* LinkedIn: https://www.linkedin.com/in/pakcyberbot/
* Medium: https://medium.com/@pakcyberbot

---

## ✨ Contributions Welcome

Want to improve it? Found a bug? PRs and issues are welcome!

