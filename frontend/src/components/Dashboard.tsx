export const Dashboard: React.FC = () => (
    <div>
      <h3 className="text-xl font-semibold mb-4">Dashboard</h3>
      <div className="space-y-4">
        <section>
          <h4 className="text-lg font-medium mb-2">Upcoming Tasks</h4>
          <ul className="list-disc pl-5">
            <li>Complete project proposal (Due: Tomorrow)</li>
            <li>Review team presentations (Due: In 2 days)</li>
          </ul>
        </section>
        <section>
          <h4 className="text-lg font-medium mb-2">Past Due</h4>
          <ul className="list-disc pl-5">
            <li>Submit expense report (Due: Yesterday)</li>
          </ul>
        </section>
      </div>
    </div>
  );