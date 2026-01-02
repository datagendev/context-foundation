# Claude Code as an "Agent Platform"

## 1. Coding Agent vs. Coding Platform

**Coding Agent/Assistant:** Claude Code is an assistant; software is the main role.

**Agent Platform:** The agent is the main role; software is the assistant to help the agent.

## 2. What Are the Differences?

### **Scripts**: Large Scripts vs. Small Tool Scripts
Unlike traditional software that builds hierarchical/dependent systems, we need to build small, modular, independent scripts that agents can easily use. **Build the toolbox.**

### **Documentation**: Explanation vs. Instruction
Unlike traditional software where documentation is often explanatory, we need to prepare documentation more like instructions—for example, style instructions or priority instructions.

## 3. How to Build an Effective Agent Platform

### 1. **File Structure**: Modular and Hierarchical
Similar to traditional software, a good file structure ensures you have a clear navigation path, which is critical for agentic search.

### 2. **CLAUDE.md**: Treat It Like a Constitution
Don't explain everything in CLAUDE.md. Treat it as a constitution to define high-level behavioral instructions. For example, instead of giving all the details on how to define ICP, tell it what the file structure looks like and what its role is so it can find ICP documentation later on.

### 3. **Git**: Version Control
Like it or not, Git will be one of the most vital skills to make your agent platform iteratable.

### 4. **Claude Code Primitives**: `/agents`, `/command`, `/skills`, `/mcp`
Claude Code provides many useful primitives that other coding-focused platforms do not provide. Use them effectively to 10x your productivity.

### 5. **Use Scripts**: Scale Your Operations
Agents do not automatically help you process thousands of data points. Use scripts to help you scale your operations.

### 6. **Least Privilege**: Minimize Secrets the Agent Can Access
Similar to how you don't want your junior engineer to have root access, try not to give direct secret access to your agent. Use MCP tools instead of API keys + APIs as much as possible.

# Quick Start

1. **Install Claude Code:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

2. **Clone the repository and start:**

```bash
git clone https://github.com/datagendev/context-foundation.git
```

3. **(Optional) Install Datagen MCP Gateway:**

```bash
curl -fsSL https://cli.datagen.dev/install.sh | sh
``` 





