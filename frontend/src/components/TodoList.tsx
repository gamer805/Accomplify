import React, { useState } from "react";
import { Button } from "./Button";

export interface Task {
    id: number;
    label: string;
    date: string;
    completed: boolean;
}
  
interface TodoListProps {
    title: string;
    tasks: Task[];
    onAddTask: (label: string, date: string) => void;
    onToggleTask: (id: number) => void;
}
  
export const TodoList: React.FC<TodoListProps> = ({ title, tasks, onAddTask, onToggleTask }) => {
    const [newTaskText, setNewTaskText] = useState('');
    const [newTaskDate, setNewTaskDate] = useState('');
  
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (newTaskText.trim() && newTaskDate) {
            onAddTask(newTaskText.trim(), newTaskDate);
            setNewTaskText('');
            setNewTaskDate('');
        }
    };
  
    return (
      <div>
        <h2 className="text-2xl font-semibold mb-4">{title}</h2>
        <form onSubmit={handleSubmit} className="mb-4 space-y-2">
          <input
            type="text"
            value={newTaskText}
            onChange={(e) => setNewTaskText(e.target.value)}
            placeholder="New task"
            className="w-full p-2 border rounded"
          />
          <input
            type="date"
            value={newTaskDate}
            onChange={(e) => setNewTaskDate(e.target.value)}
            className="w-full p-2 border rounded"
          />
          <Button onClick={() => handleSubmit} className="w-full">Add Task</Button>
        </form>
        <ul className="space-y-2">
          {tasks.map((task) => (
            <li key={task.id} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => onToggleTask(task.id)}
                className="h-5 w-5"
              />
              <span className={task.completed ? 'line-through' : ''}>{task.label}</span>
              <span className="text-sm text-gray-500">{task.date}</span>
            </li>
          ))}
        </ul>
      </div>
    );
  };