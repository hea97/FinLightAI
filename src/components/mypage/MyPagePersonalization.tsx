export function MyPagePersonalization() {
  return (
    <section className="mypage-personalization">
      <h2>내 관심 정보</h2>

      <div className="mypage-grid">
        <article>
          <h3>좋아요한 뉴스</h3>
          <p>관심 있게 저장한 뉴스를 다시 확인할 수 있습니다.</p>
        </article>

        <article>
          <h3>관심 산업</h3>
          <p>사용자가 선택한 산업의 시장 신호를 우선적으로 보여줍니다.</p>
        </article>

        <article>
          <h3>등록한 자산</h3>
          <p>내 포트폴리오와 관련된 시장 변화를 확인할 수 있습니다.</p>
        </article>

        <article>
          <h3>카카오 알림 상태</h3>
          <p>현재 연결 상태와 알림 설정을 확인할 수 있습니다.</p>
        </article>
      </div>
    </section>
  );
}
