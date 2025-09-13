// frontend/app.js
function getSession() {
	const urlParams = new URLSearchParams(window.location.search);
	const sessionFromUrl = urlParams.get("session_id");
	const input = document.getElementById("session");
	if (sessionFromUrl && input.value === "") {
		input.value = sessionFromUrl;
	}
	return input.value;
}

async function listDocs() {
	const session = getSession();
	if (!session) {
		alert(
			"Please login first and paste session_id or use the redirect query param."
		);
		return;
	}
	const res = await fetch(`/api/list_docs?session_id=${session}`);
	if (!res.ok) {
		alert("Failed to list docs: " + (await res.text()));
		return;
	}
	const data = await res.json();
	const container = document.getElementById("docs");
	container.innerHTML = "";
	data.files.forEach((f) => {
		const div = document.createElement("div");
		div.innerHTML = `<input type="checkbox" data-id="${f.id}" /> <strong>${f.name}</strong> <em style="color:gray">${f.modifiedTime || ""}</em>`;
		container.appendChild(div);
	});
}

async function addSelected() {
	const session = getSession();
	if (!session) {
		alert("No session");
		return;
	}
	const checkboxes = document.querySelectorAll(
		"#docs input[type=checkbox]:checked"
	);
	if (checkboxes.length === 0) {
		alert("Select at least one doc");
		return;
	}
	for (let cb of checkboxes) {
		const docId = cb.getAttribute("data-id");
		const form = new FormData();
		form.append("session_id", session);
		form.append("doc_id", docId);
		const res = await fetch("/api/add_doc", { method: "POST", body: form });
		const j = await res.json();
		console.log(j);
	}
	alert("Selected docs added to knowledge base.");
}

async function sendQuery() {
	const q = document.getElementById("query").value;
	if (!q) return;
	appendMessage("You", q, "you");
	const form = new FormData();
	form.append("query", q);
	const res = await fetch("/api/chat", { method: "POST", body: form });
	const j = await res.json();
	appendMessage("Bot", j.answer || JSON.stringify(j), "bot");
}

function appendMessage(who, text, cls) {
	const chat = document.getElementById("chat");
	const div = document.createElement("div");
	div.className = "message " + cls;
	div.innerHTML = `<strong>${who}:</strong> ${text}`;
	chat.appendChild(div);
	chat.scrollTop = chat.scrollHeight;
}
