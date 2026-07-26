import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

from pipeline import ask_question, generate_source_grounded_intro, generate_source_grounded_detailed
from resource_tools import find_resources
from llm import llm


class LearnMasterHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.path = "/static/index.html"
        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}

        response_data = {}
        status_code = 200

        if self.path == "/api/intro":
            topic = data.get("topic", "General Topic")
            tech_keywords = [
                "machine learning", "python", "c++", "linux", "operating system",
                "data structure", "algorithm", "software", "system design", "code",
                "ai", "git", "web", "programming", "database", "sql"
            ]
            is_tech = any(kw in topic.lower() for kw in tech_keywords)

            try:
                intro_text = generate_source_grounded_intro(topic)
            except Exception as e:
                intro_text = (
                    f"Welcome to your interactive study session on **{topic}**. "
                    "Explore key concepts, curated resources, and AI-tutored explanations below."
                )

            response_data = {
                "topic": topic,
                "introduction": intro_text,
                "is_tech": is_tech
            }

        elif self.path == "/api/detailed":
            topic = data.get("topic", "General Topic")
            try:
                content = generate_source_grounded_detailed(topic)
            except Exception as e:
                content = f"### Detailed Overview of {topic}\n\nUnable to generate details: {e}"

            response_data = {"content": content}

        elif self.path == "/api/study-plan":
            topic = data.get("topic", "General Topic")
            prompt = (
                f"Create a structured, highly practical 4-week study roadmap for mastering '{topic}'. "
                "Include:\n"
                "- **Week 1**: Foundations & Basic Setup\n"
                "- **Week 2**: Intermediate Concepts & Deep Dive\n"
                "- **Week 3**: Advanced Patterns & Architecture\n"
                "- **Week 4**: Hands-on Projects & Capstone Goal\n\n"
                "Add actionable steps and mini-milestones for each week."
            )
            try:
                res = llm.invoke(prompt)
                plan = res.content if hasattr(res, "content") else str(res)
                if isinstance(plan, list):
                    plan = "\n".join(b.get("text", "") for b in plan if isinstance(b, dict))
            except Exception as e:
                plan = (
                    f"### 4-Week Study Roadmap for {topic}\n\n"
                    "- **Week 1**: Core Foundations & Setup\n"
                    "- **Week 2**: Intermediate Concepts & Deep Dive\n"
                    "- **Week 3**: Practical Exercises & Architecture\n"
                    "- **Week 4**: Capstone Project & Practice"
                )

            response_data = {"plan": plan}

        elif self.path == "/api/resources":
            topic = data.get("topic", "General Topic")
            kind = data.get("kind", "web")
            items = find_resources(topic, kind)
            response_data = {"items": items}

        elif self.path == "/api/ask":
            topic = data.get("topic", "")
            question = data.get("question", "")
            try:
                answer = ask_question(question, topic=topic)
            except Exception:
                prompt = f"Topic: {topic}\nQuestion: {question}\nAnswer concisely as an expert study tutor."
                try:
                    res = llm.invoke(prompt)
                    answer = res.content if hasattr(res, "content") else str(res)
                    if isinstance(answer, list):
                        answer = "\n".join(b.get("text", "") for b in answer if isinstance(b, dict))
                except Exception as inner_e:
                    answer = f"Sorry, I encountered an issue: {inner_e}"
            response_data = {"answer": answer}

        else:
            status_code = 404
            response_data = {"error": "Endpoint Not Found"}

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode("utf-8"))


def run(port=5000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, LearnMasterHandler)
    print(f"LearnMaster Server running at http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run()
