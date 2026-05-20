#!/usr/bin/env node
/**
 * ADPP Session Start Hook
 * 每次 Claude Code 会话启动时自动执行
 * 注入项目上下文和当前状态
 */

const fs = require("fs");
const path = require("path");

const CWD = process.cwd();
const ADPP_DIR = path.join(CWD, ".adpp");
const CONFIG_FILE = path.join(ADPP_DIR, "config.yaml");
const PHASE_FILE = path.join(ADPP_DIR, "workspace", "current-phase.md");
const PENDING_FILE = path.join(ADPP_DIR, "workspace", "pending-approvals.log");
const COMMANDS_DIR = path.join(CWD, ".claude", "commands");

function readFile(filePath) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return null;
  }
}

function stripInlineComment(value) {
  let inSingleQuote = false;
  let inDoubleQuote = false;

  for (let i = 0; i < value.length; i++) {
    const char = value[i];
    if (char === "'" && !inDoubleQuote) inSingleQuote = !inSingleQuote;
    if (char === "\"" && !inSingleQuote) inDoubleQuote = !inDoubleQuote;

    if (char === "#" && !inSingleQuote && !inDoubleQuote) {
      return value.slice(0, i).trimEnd();
    }
  }

  return value.trimEnd();
}

function unquote(value) {
  const trimmed = value.trim();
  if (
    (trimmed.startsWith("\"") && trimmed.endsWith("\"")) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function parseSimpleYaml(content) {
  const result = {};
  const stack = [];
  const lines = content.split(/\r?\n/);

  for (const line of lines) {
    if (!line.trim() || line.trimStart().startsWith("#")) continue;
    if (line.trimStart().startsWith("- ")) continue;

    const match = line.match(/^(\s*)([^:#]+):(.*)$/);
    if (!match) continue;

    const indent = match[1].length;
    const key = match[2].trim();
    const rawValue = stripInlineComment(match[3]).trim();

    while (stack.length > 0 && stack[stack.length - 1].indent >= indent) {
      stack.pop();
    }

    if (!rawValue) {
      stack.push({ indent, key });
      continue;
    }

    const pathKey = [...stack.map((entry) => entry.key), key].join(".");
    result[pathKey] = unquote(rawValue);
  }

  return result;
}

function getAvailableCommandList() {
  if (fs.existsSync(path.join(COMMANDS_DIR, "adpp-init.md"))) {
    return "/adpp-init /adpp-prd /adpp-design /adpp-ux /adpp-implement /adpp-test /adpp-deploy /adpp-closeout /adpp-status";
  }

  if (fs.existsSync(path.join(COMMANDS_DIR, "adpp:init.md"))) {
    return "/adpp:init /adpp:prd /adpp:design /adpp:ux /adpp:implement /adpp:test /adpp:deploy /adpp:closeout /adpp:status";
  }

  return "/adpp:init /adpp:prd /adpp:design /adpp:ux /adpp:implement /adpp:test /adpp:deploy /adpp:closeout /adpp:status";
}

function main() {
  // 如果当前目录没有 .adpp，静默退出（不是 ADPP 项目）
  if (!fs.existsSync(ADPP_DIR)) {
    return;
  }

  const config = parseSimpleYaml(readFile(CONFIG_FILE) || "");
  const currentPhase = readFile(PHASE_FILE);
  const pendingLog = readFile(PENDING_FILE);

  // 读取进行中的变更
  const changesDir = path.join(ADPP_DIR, "changes");
  const activeChanges = [];
  if (fs.existsSync(changesDir)) {
    fs.readdirSync(changesDir).forEach((dir) => {
      const prdPath = path.join(changesDir, dir, "prd.md");
      if (fs.existsSync(prdPath)) {
        const prdContent = readFile(prdPath) || "";
        const statusMatch = prdContent.match(/\*\*状态\*\*:\s*(.+)/);
        const status = statusMatch ? statusMatch[1].trim() : "进行中";
        if (!status.includes("已归档")) {
          activeChanges.push({ dir, status });
        }
      }
    });
  }

  // 统计待审批的危险操作
  let pendingCount = 0;
  if (pendingLog) {
    pendingCount = (pendingLog.match(/状态: 待审批/g) || []).length;
  }

  // 构建注入内容
  const lines = [
    `<adpp-context>`,
    `ADPP 项目已检测到。以下是当前项目状态：`,
    ``,
    `项目: ${config["project.name"] || "未命名"}`,
    `技术栈: ${config["project.tech_stack"] || "未配置"}`,
  ];

  if (currentPhase) {
    lines.push(``, `当前开发状态:`, currentPhase.trim());
  }

  if (activeChanges.length > 0) {
    lines.push(``, `进行中的变更:`);
    activeChanges.forEach((c) => {
      lines.push(`  - ${c.dir}: ${c.status}`);
    });
  }

  if (pendingCount > 0) {
    lines.push(
      ``,
      `⚠️ 待审批的危险操作: ${pendingCount} 条`,
      `  运行 /adpp:status 查看详情`
    );
  }

  lines.push(
    ``,
    `可用命令: ${getAvailableCommandList()}`,
    `</adpp-context>`
  );

  // 输出到 stdout，Claude Code 会将其注入到 session context
  console.log(lines.join("\n"));
}

main();
