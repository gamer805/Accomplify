interface CategoryListProps {
    title: string;
    items: string[];
    onItemClick: (item: string) => void;
    isOpen: boolean;
    onToggle: () => void;
  }
  
export const CategoryList: React.FC<CategoryListProps> = ({ title, items, onItemClick, isOpen, onToggle }) => (
    <div className="mb-4">
        <button
            onClick={onToggle}
            className="flex items-center justify-between w-full text-left py-2 px-4 bg-gray-300 hover:bg-gray-400 rounded"
        >
            <span className="font-semibold">{title}</span>
            <span>{isOpen ? '▼' : '▶'}</span>
        </button>
        {isOpen && (
            <ul className="mt-2 space-y-1">
            {items.map((item) => (
                <li key={item}>
                <button
                    onClick={() => onItemClick(item)}
                    className="w-full text-left py-1 px-4 hover:bg-gray-300 rounded"
                >
                    {item}
                </button>
                </li>
            ))}
            </ul>
        )}
    </div>
);