import React, { useRef, useEffect } from "react";

export const DarkGridHero: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    let mouse = { x: -1000, y: -1000 };
    let smooth = { x: -1000, y: -1000 };

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };

    const handleMouseLeave = () => {
      mouse.x = -1000;
      mouse.y = -1000;
    };

    window.addEventListener("resize", handleResize);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseleave", handleMouseLeave);

    const SPACING = 34;
    const RADIUS = 150;
    const STRENGTH = 38;

    let animId: number;

    const render = () => {
      ctx.fillStyle = "#05070a";
      ctx.fillRect(0, 0, width, height);

      smooth.x += (mouse.x - smooth.x) * 0.15;
      smooth.y += (mouse.y - smooth.y) * 0.15;

      ctx.lineWidth = 1;
      ctx.strokeStyle = "#1b222d";

      // Vertical lines
      for (let x = 0; x <= width; x += SPACING) {
        ctx.beginPath();
        for (let y = 0; y <= height; y += 8) {
          const dx = x - smooth.x;
          const dy = y - smooth.y;
          const d = Math.hypot(dx, dy);
          const offset = d < RADIUS ? (dx / (d || 1)) * Math.cos((d / RADIUS) * (Math.PI / 2)) * STRENGTH : 0;
          if (y === 0) ctx.moveTo(x + offset, y);
          else ctx.lineTo(x + offset, y);
        }
        ctx.stroke();
      }

      // Horizontal lines
      for (let y = 0; y <= height; y += SPACING) {
        ctx.beginPath();
        for (let x = 0; x <= width; x += 8) {
          const dx = x - smooth.x;
          const dy = y - smooth.y;
          const d = Math.hypot(dx, dy);
          const offset = d < RADIUS ? (dy / (d || 1)) * Math.cos((d / RADIUS) * (Math.PI / 2)) * STRENGTH : 0;
          if (x === 0) ctx.moveTo(x, y + offset);
          else ctx.lineTo(x, y + offset);
        }
        ctx.stroke();
      }

      // White Spotlight
      if (smooth.x > 0 && smooth.y > 0) {
        const grad = ctx.createRadialGradient(smooth.x, smooth.y, 0, smooth.x, smooth.y, RADIUS * 1.1);
        grad.addColorStop(0, "rgba(255, 255, 255, 0.15)");
        grad.addColorStop(1, "rgba(255, 255, 255, 0)");
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(smooth.x, smooth.y, RADIUS * 1.1, 0, Math.PI * 2);
        ctx.fill();
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, []);

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-[#05070a] flex items-center justify-center font-['Virgil',cursive]">
      <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-auto" />
      <div className="relative z-10 w-[90%] max-w-[480px] flex flex-col items-center gap-3">
        <div className="bg-[#0d1117] border-2 border-white px-4 py-1 text-xs text-white uppercase tracking-wider rounded-[255px_15px_225px_15px/15px_225px_15px_255px] shadow-[3px_3px_0px_#ffffff]">
          Autonomous AI &bull; GraphRAG &bull; FastAPI
        </div>
        <div className="w-full bg-[#090d14] border-[2.5px] border-white p-6 rounded-[255px_15px_225px_15px/15px_225px_15px_255px] shadow-[6px_6px_0px_#ffffff] flex flex-col gap-4 text-white">
          <div className="border-b-2 border-dashed border-[#30363d] pb-3">
            <h1 className="text-xl font-bold">PARTH VASTAVIK</h1>
            <p className="text-xs text-[#8b949e]">GenAI Engineer & Full-Stack Architect</p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            {["FastAPI", "LangChain", "Langbase", "Neo4j", "Vector DB", "RAG Pipelines"].map((tech) => (
              <span key={tech} className="bg-[#161b22] border border-white px-2.5 py-1 rounded shadow-[2px_2px_0px_#ffffff]">
                {tech}
              </span>
            ))}
          </div>
          <a
            href="https://linkedin.com/in/sarathiparth"
            target="_blank"
            rel="noreferrer"
            className="w-full bg-white text-black font-bold py-2.5 text-center rounded-[255px_15px_225px_15px/15px_225px_15px_255px] shadow-[4px_4px_0px_rgba(255,255,255,0.4)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all"
          >
            CONNECT ON LINKEDIN &rarr;
          </a>
        </div>
      </div>
    </div>
  );
};
