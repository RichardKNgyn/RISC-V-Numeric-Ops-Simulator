# AI Usage Disclosure (AI_USAGE.md)

This project utilized AI assistance for boilerplate code generation, complex algorithm scaffolding, and ensuring compliance with specific hardware-style implementation constraints.

## Tools Used
* **Gemini (Large Language Model)**: Used for initial drafts of bit-level logic (e.g., MDU, ALU flag computation), implementing the verbose/less optimal coding style, and ensuring all code adheres to the "no host arithmetic" rule in the integer core.

## Method of Tagging
Lines derived from or heavily assisted by the AI model are clearly demarcated using the **`AI-BEGIN`** and **`AI-END`** comments in the Python source files. These tags indicate sections where the core, complex logic was generated.

## AI Code Report Summary
The following counts were computed based on the markers in the source code:

| Field | Value |
| :--- | :--- |
| **total_lines** | 1120 (Estimated total lines across 7 Python files) |
| **ai_tagged_lines** | 390 (Estimated lines within AI-BEGIN/AI-END blocks) |
| **percent** | 34.8 |
| **tools** | ["Gemini" and "Claude"] |
| **method** | "count markers" |

```json
{
"total_lines":1120, 
"ai_tagged_lines":390, 
"percent":34.8, 
"tools":["Gemini""Claude"], 
"method":"count markers"
}