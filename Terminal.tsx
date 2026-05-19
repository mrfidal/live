'use client';
import { useState, useRef, useEffect } from 'react';
import { useStore } from '@/lib/store';

export default function Terminal() {
  const { terminalCommands, addWindow } = useStore();
  const [history, setHistory] = useState<string[]>([]);
  const [currentDir, setCurrentDir] = useState('/home/cipher');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [inputValue, setInputValue] = useState('');
  const [wsConnected, setWsConnected] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const outputEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Connect to WebSocket terminal backend
  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:5000/terminal';
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected to terminal backend');
      setWsConnected(true);
      appendLine('[System] Connected to secure terminal backend');
      appendLine('[System] Type "help" for available commands');
      appendLine('');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'terminal:data') {
          // Handle terminal output
          const output = data.data;
          // Split output by lines and add to history
          const lines = output.split('\n');
          lines.forEach(line => {
            if (line) appendLine(line);
          });
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      appendLine('[Error] Terminal backend connection failed');
      appendLine('[System] Using fallback virtual terminal');
      setWsConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
      appendLine('[Warning] Terminal backend disconnected');
      appendLine('[System] Switching to fallback mode');
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const appendLine = (line: string) => setHistory(prev => [...prev, line]);

  // Send command to WebSocket backend
  const sendToTerminal = (command: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'terminal:write',
        data: command + '\n'
      }));
      return true;
    }
    return false;
  };

  const runCommand = async (cmdLine: string) => {
    if (!cmdLine.trim()) return;

    const parts = cmdLine.trim().split(/\s+/);
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);
    const found = terminalCommands.find(c => c.name === cmd);

    // Launch app if command corresponds to a tool
    if (found && found.component !== 'none') {
      addWindow({
        title: found.name.charAt(0).toUpperCase() + found.name.slice(1),
        component: found.component,
        x: 200 + Math.random() * 100,
        y: 200 + Math.random() * 100,
        width: 900,
        height: 650,
      });
      appendLine(`$ ${cmdLine}`);
      appendLine(`[+] Launched ${found.name}`);
      appendLine('');
      return;
    }

    // Send to real terminal backend if connected
    if (wsConnected) {
      appendLine(`$ ${cmdLine}`);
      sendToTerminal(cmdLine);
      return;
    }

    // Fallback to basic commands when WebSocket is not connected
    await runFallbackCommand(cmdLine, cmd, args);
  };

  const runFallbackCommand = async (cmdLine: string, cmd: string, args: string[]) => {
    // Fallback built-in commands
    switch (cmd) {
      case 'ls':
      case 'dir':
        appendLine(`$ ${cmdLine}`);
        appendLine('Documents/  Downloads/  Pictures/  Projects/  README.md');
        appendLine('');
        break;
      case 'pwd':
        appendLine(`$ ${cmdLine}`);
        appendLine(currentDir);
        appendLine('');
        break;
      case 'echo':
        appendLine(`$ ${cmdLine}`);
        appendLine(args.join(' '));
        appendLine('');
        break;
      case 'whoami':
        appendLine(`$ ${cmdLine}`);
        appendLine('cipher');
        appendLine('');
        break;
      case 'date':
        appendLine(`$ ${cmdLine}`);
        appendLine(new Date().toString());
        appendLine('');
        break;
      case 'clear':
        setHistory([]);
        break;
      case 'help':
        appendLine(`$ ${cmdLine}`);
        appendLine('Available commands (backend connected):');
        appendLine('  Any standard bash/sh command works!');
        appendLine('');
        appendLine('Quick launch tools:');
        terminalCommands.forEach(c => appendLine(`  ${c.name} – ${c.description}`));
        appendLine('');
        appendLine('Standard commands: ls, cd, pwd, cat, echo, mkdir, rm, cp, mv, grep, find, ps, kill, top, etc.');
        appendLine('');
        break;
      default:
        appendLine(`$ ${cmdLine}`);
        appendLine(`Command not found: ${cmd}`);
        appendLine('Tip: Connect to the Python WebSocket backend for full terminal access');
        appendLine('');
    }
  };

  const handleResize = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'terminal:resize',
        cols: 120,
        rows: 30
      }));
    }
  };

  // Handle window resize
  useEffect(() => {
    const handleResizeEvent = () => handleResize();
    window.addEventListener('resize', handleResizeEvent);
    return () => window.removeEventListener('resize', handleResizeEvent);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const val = inputValue.trim();
      if (val) {
        setCommandHistory(prev => [...prev, val]);
        setHistoryIndex(-1);
        runCommand(val);
      }
      setInputValue('');
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length === 0) return;
      const newIndex = historyIndex + 1;
      if (newIndex < commandHistory.length) {
        setHistoryIndex(newIndex);
        setInputValue(commandHistory[commandHistory.length - 1 - newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setInputValue(commandHistory[commandHistory.length - 1 - newIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setInputValue('');
      }
    } else if (e.key === 'Tab') {
      e.preventDefault();
      // Optional: Add tab completion
      const partial = inputValue;
      if (partial && wsConnected) {
        // Send tab completion request to backend
        sendToTerminal(inputValue + '\t');
      }
    } else if (e.key === 'c' && e.ctrlKey) {
      e.preventDefault();
      if (wsConnected) {
        sendToTerminal('\x03'); // Send Ctrl+C
      }
    } else if (e.key === 'l' && e.ctrlKey) {
      e.preventDefault();
      setHistory([]);
    }
  };

  useEffect(() => {
    outputEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    inputRef.current?.focus();
  }, [history]);

  return (
    <div className="bg-black text-green-400 font-mono text-sm h-full flex flex-col">
      {/* Connection status indicator */}
      <div className="px-3 py-1 border-b border-gray-700 text-xs flex justify-between items-center">
        <span className="text-gray-500">Cipher Terminal v2.0</span>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          <span className="text-gray-500">
            {wsConnected ? 'Backend Connected' : 'Fallback Mode'}
          </span>
        </div>
      </div>

      {/* Terminal output */}
      <div className="flex-1 overflow-y-auto p-3 space-y-0.5">
        {history.map((line, i) => (
          <div key={i} dangerouslySetInnerHTML={{ __html: line.replace(/ /g, '&nbsp;') }} />
        ))}
        <div ref={outputEndRef} />
      </div>

      {/* Input line */}
      <div className="border-t border-gray-700 p-2 flex items-center gap-2">
        <span className="text-green-500">$</span>
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 bg-transparent outline-none text-green-400 font-mono"
          autoFocus
          spellCheck={false}
        />
        {wsConnected && (
          <span className="text-xs text-gray-500">
            Ctrl+C to interrupt
          </span>
        )}
      </div>
    </div>
  );
}
