import React, { useState, ReactNode } from 'react';
import { Button } from './Button';
import { Settings } from './Settings';
import { Dashboard } from './Dashboard';
import { CategoryList } from './CategoryList';
import { TodoList, Task } from './TodoList';

const Home: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [isEditMode, setIsEditMode] = useState<boolean>(true);
  const [activeView, setActiveView] = useState<string>('tasks');
  const [activeList, setActiveList] = useState<string>('General');
  const [openCategories, setOpenCategories] = useState<Record<string, boolean>>({
    tasks: true,
    projects: true,
    events: true
  });
  const [tasks, setTasks] = useState<Record<string, Task[]>>({
    'tasks-General': [],
    'tasks-Work': [],
    'tasks-Personal': [],
    'tasks-Shopping': [],
    'projects-General': [],
    'projects-Web Development': [],
    'projects-Marketing': [],
    'projects-Research': [],
    'events-General': [],
    'events-Meetings': [],
    'events-Deadlines': [],
    'events-Birthdays': [],
  });

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);
  const toggleMode = () => setIsEditMode(!isEditMode);
  const toggleCategory = (category: string) => {
    setOpenCategories(prev => ({ ...prev, [category]: !prev[category] }));
  };

  const addTask = (text: string, date: string) => {
    const newTask: Task = {
      id: Date.now(),
      text,
      date,
      completed: false
    };
    setTasks(prev => ({
      ...prev,
      [`${activeView}-${activeList}`]: [...prev[`${activeView}-${activeList}`], newTask]
    }));
  };

  const toggleTask = (id: number) => {
    setTasks(prev => ({
      ...prev,
      [`${activeView}-${activeList}`]: prev[`${activeView}-${activeList}`].map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    }));
  };

  const categories = {
    tasks: ['General', 'Work', 'Personal', 'Shopping'],
    projects: ['General', 'Web Development', 'Marketing', 'Research'],
    events: ['General', 'Meetings', 'Deadlines', 'Birthdays']
  };

  return (
    <div className="flex h-screen flex-col">
      <header className="bg-blue-600 text-white p-4 flex justify-between items-center">
        <div className="flex items-center">
          <Button onClick={toggleSidebar} className="mr-4">
            ☰
          </Button>
          <h1 className="text-xl font-bold">Accomplify</h1>
        </div>
        <Button onClick={toggleMode}>
          {isEditMode ? 'Calendar' : 'Edit'}
        </Button>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside className={`bg-gray-200 w-64 transition-all duration-300 overflow-y-scroll ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
          <nav className="p-4">
            {(Object.keys(categories) as Array<keyof typeof categories>).map((category) => (
              <CategoryList
                key={category}
                title={category.charAt(0).toUpperCase() + category.slice(1)}
                items={categories[category]}
                onItemClick={(item) => {
                  setActiveView(category);
                  setActiveList(item);
                }}
                isOpen={openCategories[category]}
                onToggle={() => toggleCategory(category)}
              />
            ))}
            <hr className="my-4 border-t border-gray-300" />
            <Button 
              onClick={() => setActiveView('dashboard')}
              className="w-full justify-start mb-2"
            >
              Dashboard
            </Button>
            <Button 
              onClick={() => setActiveView('settings')}
              className="w-full justify-start"
            >
              Settings
            </Button>
          </nav>
        </aside>

        <main className="flex-1 p-6 overflow-auto">
          {activeView === 'dashboard' && <Dashboard />}
          {activeView === 'settings' && <Settings />}
          {['tasks', 'projects', 'events'].includes(activeView) && (
            <TodoList
              title={`${activeView.charAt(0).toUpperCase() + activeView.slice(1)}: ${activeList}`}
              tasks={tasks[`${activeView}-${activeList}`] || []}
              onAddTask={addTask}
              onToggleTask={toggleTask}
            />
          )}
        </main>
      </div>
    </div>
  );
};

export default Home;