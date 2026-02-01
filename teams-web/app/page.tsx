import Link from "next/link";

const Home = () => {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-4xl font-bold">Home</h1>
      <p className="text-lg">Hello World! This is the Home page</p>
      <p className="text-lg">
        Visit the <Link href="/about" className="text-blue-500">About</Link> page.
      </p>
    </div>
  );
};

export default Home;
