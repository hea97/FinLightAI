export function PortfolioEmptyState() {
  return (
    <section className="portfolio-empty-state">
      <div>
        <h2>아직 등록된 자산이 없습니다</h2>
        <p>
          보유 중인 자산을 추가하면 시장 신호와 함께 포트폴리오 관점의
          위험 신호를 확인할 수 있습니다.
        </p>
      </div>

      <button className="primary-cta-button" type="button">
        자산 추가하기
      </button>
    </section>
  );
}
