import { Button } from "./Button";

export const Settings: React.FC = () => (
    <div>
      <h3 className="text-xl font-semibold mb-4">Settings</h3>
      <div className="space-y-4">
        <section>
          <h4 className="text-lg font-medium mb-2">Account</h4>
          <Button onClick={() => console.log('Change password clicked')}>Change Password</Button>
        </section>
        <section>
          <h4 className="text-lg font-medium mb-2">Notifications</h4>
          <div className="flex items-center space-x-2">
            <input type="checkbox" id="emailNotifications" />
            <label htmlFor="emailNotifications">Receive email notifications</label>
          </div>
        </section>
        <section>
          <h4 className="text-lg font-medium mb-2">Theme</h4>
          <select className="border rounded p-1">
            <option>Light</option>
            <option>Dark</option>
            <option>System</option>
          </select>
        </section>
      </div>
    </div>
  );