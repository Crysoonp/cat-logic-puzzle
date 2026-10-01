/*
 * ねこみちロジック 長期ストーリー設定
 * Version: Story Bible 2026-10-01
 *
 * このファイルは物語設定の保存用です。
 * 現在のゲームへ自動で読み込ませる前提ではありません。
 * 内容を変更するときは STORY_BIBLE.md も同時に更新してください。
 */

window.NEKOMICHI_STORY_BIBLE = {
  updatedAt: "2026-10-01",
  coreTheme: "母への帰り道を探す旅から、どんな猫にも帰れる道と場所を作る物語へ成長する。",
  keyword: {
    word: "道",
    earlyUse: "ステージ2～3付近で、ニャンじいが自然な台詞として一度だけ印象づける。",
    avoid: "血筋や特殊能力を序盤から露骨に説明しない。タイジュ以降も『道』を連呼しない。",
    lineCandidates: [
      "迷っている猫を見つけたら、正しい道へ導いてやるんじゃぞ。",
      "焦らんでよい。ひとつずつ道を見つけていけばよいんじゃ。"
    ]
  },
  parts: [
    {
      id: 1,
      title: "お母さんへの帰り道",
      stages: "1-1000",
      goal: "母ミヤを探し、別れの真相を知る。",
      milestones: [
        { stage: 50, event: "タイジュが仲間になり、猫じゃらしを解放" },
        { stage: 100, event: "第2の仲間と、第2のヒント" },
        { stage: 150, event: "第3の仲間と、肉球チェック" },
        { stage: 200, event: "第4の仲間と、ネコ缶。基本ヒントが揃う" },
        { stage: 500, event: "母を知る者への導線。『知りたきゃ、ついてこい』" },
        { stage: 600, event: "母の名前がミヤだと判明" },
        { stage: 999, event: "超ボスにゃんこと対峙し、ミヤの戦友だと判明" },
        { stage: 1000, event: "ミヤと再会。年の離れた兄の存在を知る" }
      ]
    },
    {
      id: 2,
      title: "兄が残した足あと",
      stages: "1001-3000",
      goal: "困っている猫を助けながら、年の離れた兄を探す。",
      milestones: [
        { stage: 1400, event: "兄の最初の足あとと協力者を知る" },
        { stage: 1900, event: "テコちゃん自身が救助を優先するようになる" },
        { stage: 2400, event: "兄が足あとを隠している可能性が判明" },
        { stage: 2999, event: "兄へ続く最後の道を完成" },
        { stage: 3000, event: "年の離れた兄と再会" }
      ]
    }
  ],
  characters: {
    teko: { name: "テコちゃん", role: "主人公" },
    miya: { name: "ミヤ", role: "母。超ボスにゃんこの戦友" },
    nyanjii: { name: "ニャンじい", role: "育ての親。ミヤからテコちゃんを託された" },
    taiju: { name: "タイジュ", joinStage: 50, role: "森と迷子の猫を守る", hint: "猫じゃらし" },
    superBoss: { name: null, role: "過去の共同体の指導者。ミヤの戦友", status: "名前未定" },
    olderBrother: { name: null, role: "年の離れた兄。各地で困っている猫を助ける", status: "名前未定" }
  },
  companionSlots: [
    { stage: 100, name: null, motif: ["湖", "水辺", "記録", "地図", "論理"], hint: "またたび", status: "過去案の湖系名称を要確認" },
    { stage: 150, name: null, motif: ["観察", "見張り", "誤りの発見"], hint: "肉球チェック" },
    { stage: 200, name: null, motif: ["声", "気配", "救助対象の発見"], hint: "ネコ缶" }
  ],
  otherAnimalsPolicy: {
    principle: "猫中心の世界を保ち、他の動物を無制限に増やさない。",
    crows: "物や情報を持ち去る、噂をかき乱す。一部は敵対、一部は協力。",
    foxes: "道や情報を惑わせる。嘘と本当を混ぜる。一部は敵対、一部は協力。",
    restriction: "犬、熊、鶏などは、物語上の明確な役割がある場合だけ追加する。"
  }
};
