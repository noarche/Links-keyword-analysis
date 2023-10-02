import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from bs4 import BeautifulSoup
import requests
from collections import Counter

def paste_to_input():
    input_box.delete("1.0", tk.END)
    input_box.insert(tk.END, app.clipboard_get())

def copy_results():
    app.clipboard_clear()
    app.clipboard_append(results_box.get("1.0", tk.END))

def save_results():
    file_name = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_name:
        with open(file_name, "w") as file:
            file.write(results_box.get("1.0", tk.END))
        messagebox.showinfo("Info", "Results saved successfully!")

def analyze_link(link, word_counter, idx):
    try:
        verify_ssl = not ignore_ssl_var.get()
        response = requests.get(link, verify=verify_ssl, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        meta_content = soup.find("meta", {"name": "keywords"})
        if meta_content and meta_content.get("content"):
            for word in meta_content["content"].split(","):
                word_counter[word.strip().lower()] += 1
    except (requests.exceptions.SSLError, requests.exceptions.RequestException, requests.exceptions.Timeout):
        pass  # Ignore SSL errors, timeouts, and other request-related exceptions
    finally:
        progress_bar["value"] += 1
        update_progress_label(idx, len(links))
        app.update_idletasks()

    if idx < len(links):
        app.after(1, analyze_link, links[idx], word_counter, idx + 1)
    else:
        display_results(word_counter)

def display_results(word_counter):
    total_words = sum(word_counter.values())
    results = [(word, count, (count / total_words) * 100) for word, count in word_counter.items()]
    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)

    results_box.delete("1.0", tk.END)
    for word, count, percentage in sorted_results:
        results_box.insert(tk.END, f"'{word}': {count} times ({percentage:.2f}% of total words)\n")

def analyze_links():
    global links
    links = input_box.get("1.0", tk.END).strip().splitlines()
    word_counter = Counter()

    progress_bar["maximum"] = len(links)
    progress_bar["value"] = 0
    update_progress_label(0, len(links))
    
    # Begin asynchronous processing
    app.after(1, analyze_link, links[0], word_counter, 1)

def update_progress_label(current, total):
    progress_label.config(text=f"Scraped {current}/{total} links")

app = tk.Tk()
app.title("Link Analyzer")

# Labels
tk.Label(app, text="Input").pack(pady=5)
input_box = tk.Text(app, height=10, width=50)
input_box.pack(pady=5)

tk.Label(app, text="Results").pack(pady=5)
results_box = tk.Text(app, height=10, width=50)
results_box.pack(pady=5)

# Progress Bar
progress_bar = ttk.Progressbar(app, orient='horizontal', length=300, mode='determinate')
progress_bar.pack(pady=5)

# Progress label
progress_label = tk.Label(app, text="")
progress_label.pack(pady=5)

# Buttons
paste_button = tk.Button(app, text="Paste to Input", command=paste_to_input)
paste_button.pack(pady=5)

copy_button = tk.Button(app, text="Copy Results", command=copy_results)
copy_button.pack(pady=5)

save_button = tk.Button(app, text="Save Results", command=save_results)
save_button.pack(pady=5)

analyze_button = tk.Button(app, text="Analyze Links", command=analyze_links)
analyze_button.pack(pady=5)

# Checkbox to ignore SSL
ignore_ssl_var = tk.BooleanVar()
ignore_ssl_checkbutton = tk.Checkbutton(app, text="Ignore SSL", variable=ignore_ssl_var)
ignore_ssl_checkbutton.pack(pady=5)

app.mainloop()
