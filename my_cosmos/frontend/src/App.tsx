export default function App() {
  return (
    <main className="container-cosmos py-16">
      <p className="eyebrow">Space Research Intelligence</p>
      <h1 className="mt-2 text-5xl font-bold">
        Hello, <span className="text-violet-500">COSMOS</span>
      </h1>
      <p className="mt-4 max-w-xl text-lg text-navy-500">Explore humanity's knowledge beyond Earth.</p>

      <div className="glass mt-10 max-w-md p-6">
        <p className="font-semibold">This is a glass card</p>
        <p className="mt-1 text-sm text-navy-500">Frosted white, soft shadow, rounded corners.</p>
      </div>

      <div className="mt-6 flex gap-3">
        <span className="h-12 w-12 rounded-full bg-lavender-200" title="lavender" />
        <span className="h-12 w-12 rounded-full bg-dusty-200" title="dusty blue" />
        <span className="h-12 w-12 rounded-full bg-blush-200" title="blush" />
        <span className="h-12 w-12 rounded-full bg-mint-200" title="mint" />
      </div>
    </main>
  );
}
