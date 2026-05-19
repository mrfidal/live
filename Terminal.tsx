'use client';
import { useState, useRef, useEffect } from 'react';
import { useStore } from '@/lib/store';

export default function Terminal() {
  const { terminalCommands, addWindow } = useStore();
  const [history, setHistory] = useState<string[]>([]);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [inputValue, setInputValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const outputEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:5000/terminal');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('Connected to terminal backend');
      setHistory(prev => [...prev, '\x1b[32mConnected to secure terminal\x1b[0m', '']);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'terminal:data') {
        setHistory(prev => {
          const lastIndex = prev.length - 1;
          if (prev[lastIndex] && !prev[lastIndex].endsWith('\n') && data.data.includes('\n')) {
            const newHistory = [...prev];
            const parts = data.data.split('\n');
            newHistory[lastIndex] = newHistory[lastIndex] + parts[0];
            for (let i = 1; i < parts.length - 1; i++) {
              newHistory.push(parts[i]);
            }
            if (parts[parts.length - 1]) {
              newHistory.push(parts[parts.length - 1]);
            }
            return newHistory;
          } else {
            const lines = data.data.split('\n');
            const newHistory = [...prev];
            for (let i = 0; i < lines.length - 1; i++) {
              newHistory.push(lines[i]);
            }
            if (lines[lines.length - 1]) {
              newHistory.push(lines[lines.length - 1]);
            }
            return newHistory;
          }
        });
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setHistory(prev => [...prev, '\x1b[31mFailed to connect to terminal backend\x1b[0m', '']);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setHistory(prev => [...prev, '\x1b[31mTerminal backend disconnected\x1b[0m', '']);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const sendCommand = (command: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'terminal:write',
        data: command + '\n'
      }));
      return true;
    }
    return false;
  };

  const runCommand = (cmdLine: string) => {
    if (!cmdLine.trim()) return;

    const parts = cmdLine.trim().split(/\s+/);
    const cmd = parts[0].toLowerCase();
    const found = terminalCommands.find(c => c.name === cmd);

    if (found && found.component !== 'none') {
      addWindow({
        title: found.name.charAt(0).toUpperCase() + found.name.slice(1),
        component: found.component,
        x: 200 + Math.random() * 100,
        y: 200 + Math.random() * 100,
        width: 900,
        height: 650,
      });
      setHistory(prev => [...prev, `$ ${cmdLine}`, `\x1b[32m[+] Launched ${found.name}\x1b[0m`, '']);
      setInputValue('');
      return;
    }

    setHistory(prev => [...prev, `$ ${cmdLine}`]);
    sendCommand(cmdLine);
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const val = inputValue.trim();
      if (val) {
        setCommandHistory(prev => [...prev, val]);
        setHistoryIndex(-1);
        runCommand(val);
      }
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
    } else if (e.key === 'c' && e.ctrlKey) {
      e.preventDefault();
      sendCommand('\x03');
    } else if (e.key === 'l' && e.ctrlKey) {
      e.preventDefault();
      setHistory([]);
    }
  };

  useEffect(() => {
    outputEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    inputRef.current?.focus();
  }, [history]);

  const stripAnsi = (text: string) => {
    return text.replace(/[\u001b\u009b][[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><]/g, '');
  };

  return (
    <div className="bg-black text-green-400 font-mono text-sm h-full flex flex-col">
      <div className="flex-1 overflow-y-auto p-3">
        {history.map((line, i) => (
          <div key={i} className="whitespace-pre-wrap">
            {stripAnsi(line)}
          </div>
        ))}
        <div ref={outputEndRef} />
      </div>
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
      </div>
    </div>
  );
}
