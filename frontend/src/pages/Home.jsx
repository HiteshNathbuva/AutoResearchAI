import MainLayout from "../layouts/MainLayout";

import HeroSection from "../components/research/HeroSection";
import ResearchInput from "../components/research/ResearchInput";
import WorkflowProgress from "../components/research/WorkflowProgress";
import ResearchResult from "../components/research/ResearchResult";

function Home() {
  return (
    <MainLayout>
      <div className="flex flex-col gap-16">

        {/* Hero Section */}
        <HeroSection />

        {/* Research Workspace */}
        <ResearchInput />

        {/* Workflow Progress */}
        <WorkflowProgress />

        {/* Research Result */}
        <ResearchResult />

      </div>
    </MainLayout>
  );
}

export default Home;