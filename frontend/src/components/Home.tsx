import React, { useState, useEffect } from 'react';
import { Button } from './Button';
import { Settings } from './Settings';
import { Dashboard } from './Dashboard';
import { CategoryList } from './CategoryList';
import { TodoList, Task } from './TodoList';
import Login from './Login';

interface User {
  user_id: number;
  name: string;
  email: string;
  picture: string;
}

interface Categories {
  tasks: string[];
  projects: string[];
  events: string[];
}

const categories: Categories = {
  tasks: ['General', 'Work', 'Personal', 'Shopping'],
  projects: ['General', 'Web Development', 'Marketing', 'Research'],
  events: ['General', 'Meetings', 'Deadlines', 'Birthdays']
};

const Home: React.FC = () => {
  // State declarations
  const [user, setUser] = useState<User | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isEditMode, setIsEditMode] = useState(true);
  const [activeView, setActiveView] = useState('tasks');
  const [activeList, setActiveList] = useState('General');
  const [openCategories, setOpenCategories] = useState<Record<keyof Categories, boolean>>({
    tasks: true,
    projects: true,
    events: true
  });
  const [tasks, setTasks] = useState<Record<string, Task[]>>({
    'tasks-General': [], 'tasks-Work': [], 'tasks-Personal': [], 'tasks-Shopping': [],
    'projects-General': [], 'projects-Web Development': [], 'projects-Marketing': [], 'projects-Research': [],
    'events-General': [], 'events-Meetings': [], 'events-Deadlines': [], 'events-Birthdays': [],
  });
  const [showLoginModal, setShowLoginModal] = useState(false);

  // Event handlers
  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);
  const toggleMode = () => setIsEditMode(!isEditMode);
  const toggleCategory = (category: keyof Categories) => {
    setOpenCategories(prev => ({ ...prev, [category]: !prev[category] }));
  };

  const handleLoginSuccess = (loggedInUser: User) => {
    setUser(loggedInUser);
    setShowLoginModal(false);
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  const addTask = (label: string, date: string) => {
    const newTask: Task = { id: Date.now(), label, date, completed: false };
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

  // API calls
  const updateTaskList = async () => {
    try {
      const token = localStorage.getItem('token');
      if (user) {
        const options = { name: activeList, category: activeView, tasks: tasks[`${activeView}-${activeList}`], email: user?.email };
        const response = await fetch(`${process.env.REACT_APP_BACKEND_API}api/save_tasklist/`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
          },
          body: JSON.stringify(options)
        });
        if (!response.ok) throw new Error('Network response was not ok');
      }
      
    } catch (error) {
      console.error('Error updating task list:', error);
    }
  };

  const loadTaskList = async () => {
    try {
      const token = localStorage.getItem('token');
      if (user) {
        const options = { user_email: user?.email };
        const response = await fetch(`${process.env.REACT_APP_BACKEND_API}api/get_tasklist/`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
          },
          body: JSON.stringify(options)
        });
        const data = await response.json();
        console.log(data.task_collection)
        setTasks({...tasks, ...data.task_collection})
        if (!response.ok) throw new Error('Network response was not ok');
      }
      
    } catch (error) {
      console.error('Error recieving task list:', error);
    }
  }

  // Effects
  useEffect(() => {
    console.log("Tasks Retrieved.");
    updateTaskList();
  }, [tasks, activeView, activeList]);

  useEffect(() => {
    console.log("User: ", user);
    if (user) {
      loadTaskList();
    }
  }, [user])

  // Render methods
  const renderSidebar = () => (
    <aside className={`bg-gray-200 w-64 transition-all duration-300 overflow-y-scroll ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
      <nav className="p-4">
        {(Object.keys(categories) as Array<keyof Categories>).map((category) => (
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
        <Button onClick={() => setActiveView('dashboard')} className="w-full justify-start mb-2">
          Dashboard
        </Button>
        <Button onClick={() => setActiveView('settings')} className="w-full justify-start">
          Settings
        </Button>
      </nav>
    </aside>
  );

  const renderMainContent = () => (
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
  );

  // Main render
  return (
    <div className="flex h-screen flex-col">
      <header className="bg-blue-600 text-white p-4 flex justify-between items-center">
        <div className="flex items-center">
          <Button onClick={toggleSidebar} className="mr-4">☰</Button>
          <h1 className="text-xl font-bold">Accomplify</h1>
        </div>
        <div className="flex items-center">
          <Button onClick={toggleMode} className="mr-4">{isEditMode ? 'Calendar' : 'Edit'}</Button>
          {user ? (
            <div className="flex items-center">
              <span className="mr-4">Welcome, {user.name}!</span>
              <Button onClick={handleLogout}>Logout</Button>
            </div>
          ) : (
            <Button onClick={() => setShowLoginModal(true)}>Login</Button>
          )}
        </div>
      </header>
      <div className="flex flex-1 overflow-hidden">
        {renderSidebar()}
        {renderMainContent()}
      </div>
      {showLoginModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg">
            <Login onLoginSuccess={handleLoginSuccess} />
            <Button onClick={() => setShowLoginModal(false)} className="mt-4">Close</Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;