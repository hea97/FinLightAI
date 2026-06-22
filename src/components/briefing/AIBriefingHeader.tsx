type AIBriefingHeaderProps = {
  generatedAt: string;
  updatedAt: string;
};

export function AIBriefingHeader({ generatedAt, updatedAt }: AIBriefingHeaderProps) {
  return (
    <header className="ai-briefing-header">
      <div>
        <h2>오늘의 AI 시장 브리핑</h2>
        <p>시장 신호와 주요 이슈를 요약한 브리핑입니다.</p>
      </div>

      <span className="briefing-date">
        기준일: {generatedAt} · 마지막 업데이트: {updatedAt}
      </span>
    </header>
  );
}
