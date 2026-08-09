# フォニックスアイランド キャラクター・ロースター

幼児向け英語学習動画用キャラクター設定。各音素を「役職＋名詞」の同音ペアで表現し、同じ音で始まる動詞を使った行動の歌でフォニックス導入を行う。

## 設計ルール

1. **命名**: `[Role] + [Character noun]` どちらも同じ音素で始まる
2. **動物縛りなし**: 物・食べ物・概念でも可
3. **歌**: そのキャラが、同じ音素で始まる動詞を使って行動する
4. **対象**: 幼児（フォニックス導入段階）

## AI音楽生成時の表記ルール ⚠️

歌詞は AI音楽生成ツール（Suno/Udio 等）で歌わせることを想定。単独の `A-A-A!` のような表記は AI に音素読み（アー）されやすいため、**文字名読み（letter name）を英語スペルで明記**する。

| 文字 | 表記 | 読み | 文字 | 表記 | 読み |
|---|---|---|---|---|---|
| A | Ay | エイ | N | En | エヌ |
| B | Bee | ビー | O | Oh | オウ |
| C | See | スィー | P | Pee | ピー |
| D | Dee | ディー | Q | Cue | キュー |
| E | Ee | イー | R | Ar | アー |
| F | Eff | エフ | S | Ess | エス |
| G | Gee | ジー | T | Tee | ティー |
| H | Aitch | エイチ | U | You | ユー |
| I | Eye | アイ | V | Vee | ヴィー |
| J | Jaye | ジェイ | W | Double-U | ダブリュー |
| K | Kay | ケイ | X | Ex | エックス |
| L | Ell | エル | Y | Why | ワイ |
| M | Em | エム | Z | Zee | ズィー |

※ Z は米式 "Zee"。英式の場合は "Zed" に置き換え。

## 26音 ロースター

| 音 | キャラクター | 主な動詞 |
|---|---|---|
| A /æ/ | **Aunt Ant**（おばさんアリ） | ask, add, act, applaud, answer |
| B /b/ | **Baker Bear**（パン屋クマ） | bake, blow, bounce, build, bring |
| C /k/ | **Cowboy Cat**（カウボーイ猫） | catch, call, climb, count, cook |
| D /d/ | **Doctor Dragon**（医者ドラゴン） | dance, draw, dig, dive, drop |
| E /e/ | **Engineer Egg**（エンジニアたまご） | enter, end, echo, edit, exercise |
| F /f/ | **Fisher Frog**（漁師カエル） | fish, fly, flip, find, fix |
| G /g/ | **Guardian Goat**（守護者ヤギ） | grow, give, get, go, grab |
| H /h/ | **Hiker Hippo**（ハイカーカバ） | hop, hug, hold, help, hide |
| I /ɪ/ | **Inventor Ice**（発明家アイス） | invent, imagine, imitate, inspect, itch |
| J /dʒ/ | **Juggler Jellyfish**（大道芸人クラゲ） | jump, juggle, join, jog |
| K /k/ | **King Kangaroo**（王様カンガルー） | kick, keep, kiss, knock |
| L /l/ | **Librarian Lion**（司書ライオン） | look, listen, laugh, love, learn |
| M /m/ | **Magician Mouse**（魔術師ネズミ） | make, march, move, mix, melt |
| N /n/ | **Ninja Nut**（忍者ナット） | nod, nap, name, nibble, knock |
| O /ɒ/ | **Outlaw Octopus**（アウトロータコ） | open, offer, observe, order |
| P /p/ | **Pilot Panda**（パイロットパンダ） | paint, push, pull, play, pack |
| Q /kw/ | **Queen Quiz**（？マークの女王様） | quiz, question, quit, quiver, quack |
| R /r/ | **Runner Rabbit**（ランナーウサギ） | run, roll, ride, read, reach |
| S /s/ | **Singer Snake**（歌手ヘビ） | sing, see, sit, swim, sip |
| T /t/ | **Teacher Tacos**（先生タコス） | teach, tap, throw, talk, touch |
| U /ʌ/ | **Uncle Unicorn**（ユニコーンおじさん） | unzip, unlock, untie, unfold, unbutton |
| V /v/ | **Viking Virus**（バイキングウイルス） | visit, vote, vacuum, vanish, vroom |
| W /w/ | **Waiter Wolf**（給仕オオカミ） | walk, wait, wave, wash, want |
| X /ks/ | **Boxer Fox**（ボクサーキツネ） | box, fix, mix, wax（語末 x） |
| Y /j/ | **Yoga Yeti**（ヨガする雪男） | yawn, yell, yodel, yank, yap |
| Z /z/ | **Zigzag Zebra**（ジグザグシマウマ） | zip, zoom, zigzag, zonk |

### 補足メモ
- **A**: "aunt" /ænt/ と "ant" /ænt/ は米英語で同音。フォニックス導入の理想形
- **I**: "inventor" /ɪ/ は短母音、"ice cream" /aɪ/ は長母音だが、文字 I 導入として採用
- **Q**: ？マークの形状をそのまま身体にし、王冠を載せたビジュアル
- **X**: 語頭 /ks/ の単語が極端に少ないため、語末 x を活用

## 歌のテンプレート

```
[文字名]! [文字名]! [文字名]! [キャラ名]!
What can [キャラ名] do?
[verb1]! [verb2]! [verb3]! [verb4]!
[キャラ名] [verb5]s too!

[キャラ名] [verb1]s the [もの],
[キャラ名] [verb2]s the [もの],
[キャラ名] [verb3]s up high,
[キャラ名] [verb4]s — oh my!

[文字名]! [文字名]! [文字名]! Now you try!
[verb1]! [verb2]! [verb3]! [verb4]!
```

※ `[文字名]` は letter name のスペル（A→Ay, B→Bee, C→See, ...）。詳細は上の表を参照。

## 各キャラクターの歌詞（26曲）

### 🎵 Aunt Ant's Ay-Ay-Ay Song
```
Ay! Ay! Ay! Aunt Ant!
What can Aunt Ant do?
Ask! Add! Act! Applaud!
Aunt Ant answers too!

Aunt Ant asks a question,
Aunt Ant adds with action,
Aunt Ant acts out loud,
Aunt Ant applauds the crowd!

Ay! Ay! Ay! Now you try!
Ask! Add! Act! Applaud!
```

### 🎵 Baker Bear's Bee-Bee-Bee Song
```
Bee! Bee! Bee! Baker Bear!
What can Baker Bear do?
Bake! Blow! Bounce! Build!
Baker Bear builds it too!

Baker Bear bakes the bread,
Baker Bear blows the bed,
Baker Bear bounces the ball,
Baker Bear builds it tall!

Bee! Bee! Bee! Now you try!
Bake! Blow! Bounce! Build!
```

### 🎵 Cowboy Cat's See-See-See Song
```
See! See! See! Cowboy Cat!
What can Cowboy Cat do?
Catch! Call! Climb! Count!
Cowboy Cat cooks too!

Cowboy Cat catches a cow,
Cowboy Cat calls out "wow!",
Cowboy Cat climbs the cliff,
Cowboy Cat counts in a jiff!

See! See! See! Now you try!
Catch! Call! Climb! Count!
```

### 🎵 Doctor Dragon's Dee-Dee-Dee Song
```
Dee! Dee! Dee! Doctor Dragon!
What can Doctor Dragon do?
Dance! Draw! Dig! Dive!
Doctor Dragon does it too!

Doctor Dragon dances down,
Doctor Dragon draws a crown,
Doctor Dragon digs a hole,
Doctor Dragon dives — go go go!

Dee! Dee! Dee! Now you try!
Dance! Draw! Dig! Dive!
```

### 🎵 Engineer Egg's Ee-Ee-Ee Song
```
Ee! Ee! Ee! Engineer Egg!
What can Engineer Egg do?
Enter! End! Echo! Edit!
Engineer Egg exercises too!

Engineer Egg enters the door,
Engineer Egg ends the chore,
Engineer Egg echoes "hooray!",
Engineer Egg edits the day!

Ee! Ee! Ee! Now you try!
Enter! End! Echo! Edit!
```

### 🎵 Fisher Frog's Eff-Eff-Eff Song
```
Eff! Eff! Eff! Fisher Frog!
What can Fisher Frog do?
Fish! Fly! Flip! Find!
Fisher Frog finds it too!

Fisher Frog fishes for fun,
Fisher Frog flies in the sun,
Fisher Frog flips up high,
Fisher Frog finds a fly!

Eff! Eff! Eff! Now you try!
Fish! Fly! Flip! Find!
```

### 🎵 Guardian Goat's Gee-Gee-Gee Song
```
Gee! Gee! Gee! Guardian Goat!
What can Guardian Goat do?
Grow! Give! Grab! Go!
Guardian Goat gets it too!

Guardian Goat grows a tree,
Guardian Goat gives to me,
Guardian Goat grabs the rake,
Guardian Goat goes — for goodness sake!

Gee! Gee! Gee! Now you try!
Grow! Give! Grab! Go!
```

### 🎵 Hiker Hippo's Aitch-Aitch-Aitch Song
```
Aitch! Aitch! Aitch! Hiker Hippo!
What can Hiker Hippo do?
Hop! Hug! Hold! Hide!
Hiker Hippo helps you too!

Hiker Hippo hops on the hill,
Hiker Hippo hugs with a thrill,
Hiker Hippo holds your hand,
Hiker Hippo hides in the sand!

Aitch! Aitch! Aitch! Now you try!
Hop! Hug! Hold! Hide!
```

### 🎵 Inventor Ice's Eye-Eye-Eye Song
```
Eye! Eye! Eye! Inventor Ice!
What can Inventor Ice do?
Invent! Imagine! Imitate! Inspect!
Inventor Ice itches too!

Inventor Ice invents a treat,
Inventor Ice imagines a beat,
Inventor Ice imitates a clown,
Inventor Ice inspects the town!

Eye! Eye! Eye! Now you try!
Invent! Imagine! Imitate! Inspect!
```

### 🎵 Juggler Jellyfish's Jaye-Jaye-Jaye Song
```
Jaye! Jaye! Jaye! Juggler Jellyfish!
What can Juggler Jellyfish do?
Jump! Juggle! Join! Jog!
Juggler Jellyfish judges too!

Juggler Jellyfish jumps with joy,
Juggler Jellyfish juggles a toy,
Juggler Jellyfish joins the line,
Juggler Jellyfish jogs — feels fine!

Jaye! Jaye! Jaye! Now you try!
Jump! Juggle! Join! Jog!
```

### 🎵 King Kangaroo's Kay-Kay-Kay Song
```
Kay! Kay! Kay! King Kangaroo!
What can King Kangaroo do?
Kick! Keep! Kiss! Knock!
King Kangaroo kneels too!

King Kangaroo kicks the can,
King Kangaroo keeps a fan,
King Kangaroo kisses the queen,
King Kangaroo knocks — what a scene!

Kay! Kay! Kay! Now you try!
Kick! Keep! Kiss! Knock!
```

### 🎵 Librarian Lion's Ell-Ell-Ell Song
```
Ell! Ell! Ell! Librarian Lion!
What can Librarian Lion do?
Look! Listen! Laugh! Learn!
Librarian Lion loves you too!

Librarian Lion looks at a book,
Librarian Lion listens — take a look,
Librarian Lion laughs out loud,
Librarian Lion learns from the crowd!

Ell! Ell! Ell! Now you try!
Look! Listen! Laugh! Learn!
```

### 🎵 Magician Mouse's Em-Em-Em Song
```
Em! Em! Em! Magician Mouse!
What can Magician Mouse do?
Make! March! Move! Mix!
Magician Mouse melts too!

Magician Mouse makes a hat,
Magician Mouse marches on the mat,
Magician Mouse moves the stars,
Magician Mouse mixes some jars!

Em! Em! Em! Now you try!
Make! March! Move! Mix!
```

### 🎵 Ninja Nut's En-En-En Song
```
En! En! En! Ninja Nut!
What can Ninja Nut do?
Nod! Nap! Nibble! Knock!
Ninja Nut names you too!

Ninja Nut nods in the night,
Ninja Nut naps out of sight,
Ninja Nut nibbles a snack,
Ninja Nut knocks — tap-tap-tap!

En! En! En! Now you try!
Nod! Nap! Nibble! Knock!
```

### 🎵 Outlaw Octopus's Oh-Oh-Oh Song
```
Oh! Oh! Oh! Outlaw Octopus!
What can Outlaw Octopus do?
Open! Offer! Observe! Order!
Outlaw Octopus operates too!

Outlaw Octopus opens the door,
Outlaw Octopus offers some more,
Outlaw Octopus observes the sky,
Outlaw Octopus orders — oh my!

Oh! Oh! Oh! Now you try!
Open! Offer! Observe! Order!
```

### 🎵 Pilot Panda's P-P-P Song
```
P! P! P! Pilot Panda!
What can Pilot Panda do?
Paint! Push! Pull! Play!
Pilot Panda packs too!

Pilot Panda paints the plane,
Pilot Panda pushes the train,
Pilot Panda pulls the rope,
Pilot Panda plays — there's hope!

P! P! P! Now you try!
Paint! Push! Pull! Play!
```

### 🎵 Queen Quiz's Cue-Cue-Cue Song
```
Cue! Cue! Cue! Queen Quiz!
What can Queen Quiz do?
Quiz! Question! Quit! Quiver!
Queen Quiz quacks too!

Queen Quiz quizzes the class,
Queen Quiz questions — who will pass?
Queen Quiz quivers with delight,
Queen Quiz quacks all night!

Cue! Cue! Cue! Now you try!
Quiz! Question! Quit! Quiver!
```

### 🎵 Runner Rabbit's Ar-Ar-Ar Song
```
Ar! Ar! Ar! Runner Rabbit!
What can Runner Rabbit do?
Run! Roll! Ride! Read!
Runner Rabbit reaches too!

Runner Rabbit runs so fast,
Runner Rabbit rolls — what a blast,
Runner Rabbit rides a bike,
Runner Rabbit reads what you like!

Ar! Ar! Ar! Now you try!
Run! Roll! Ride! Read!
```

### 🎵 Singer Snake's Ess-Ess-Ess Song
```
Ess! Ess! Ess! Singer Snake!
What can Singer Snake do?
Sing! See! Sit! Sip!
Singer Snake swims too!

Singer Snake sings a song,
Singer Snake sees all along,
Singer Snake sits on a rock,
Singer Snake sips — tick tock!

Ess! Ess! Ess! Now you try!
Sing! See! Sit! Sip!
```

### 🎵 Teacher Tacos's Tee-Tee-Tee Song
```
Tee! Tee! Tee! Teacher Tacos!
What can Teacher Tacos do?
Teach! Tap! Throw! Touch!
Teacher Tacos talks too!

Teacher Tacos teaches ten,
Teacher Tacos taps again,
Teacher Tacos throws the ball,
Teacher Tacos talks to all!

Tee! Tee! Tee! Now you try!
Teach! Tap! Throw! Touch!
```

### 🎵 Uncle Unicorn's You-You-You Song
```
You! You! You! Uncle Unicorn!
What can Uncle Unicorn do?
Unzip! Unlock! Untie! Unfold!
Uncle Unicorn unbuttons too!

Uncle Unicorn unzips the bag,
Uncle Unicorn unlocks the tag,
Uncle Unicorn unties the bow,
Uncle Unicorn unfolds — let's go!

You! You! You! Now you try!
Unzip! Unlock! Untie! Unfold!
```

### 🎵 Viking Virus's Vee-Vee-Vee Song
```
Vee! Vee! Vee! Viking Virus!
What can Viking Virus do?
Visit! Vote! Vacuum! Vanish!
Viking Virus vrooms too!

Viking Virus visits a friend,
Viking Virus votes with courage,
Viking Virus vacuums the floor,
Viking Virus vanishes — out the door!

Vee! Vee! Vee! Now you try!
Visit! Vote! Vacuum! Vanish!
```

### 🎵 Waiter Wolf's Double-U Song
```
Double-U! Double-U! Double-U! Waiter Wolf!
What can Waiter Wolf do?
Walk! Wait! Wave! Wash!
Waiter Wolf wants you too!

Waiter Wolf walks to the door,
Waiter Wolf waits some more,
Waiter Wolf waves "hello!",
Waiter Wolf washes — let's go!

Double-U! Double-U! Double-U! Now you try!
Walk! Wait! Wave! Wash!
```

### 🎵 Boxer Fox's Ex-Ex-Ex Song
```
Ex! Ex! Ex! Boxer Fox!
What can Boxer Fox do?
Box! Fix! Mix! Wax!
Boxer Fox checks too!

Boxer Fox boxes in the ring,
Boxer Fox fixes everything,
Boxer Fox mixes the paint,
Boxer Fox waxes — no complaint!

Ex! Ex! Ex! Now you try!
Box! Fix! Mix! Wax!
```

### 🎵 Yoga Yeti's Why-Why-Why Song
```
Why! Why! Why! Yoga Yeti!
What can Yoga Yeti do?
Yawn! Yell! Yodel! Yank!
Yoga Yeti yaps too!

Yoga Yeti yawns so wide,
Yoga Yeti yells with pride,
Yoga Yeti yodels high,
Yoga Yeti yanks the sky!

Why! Why! Why! Now you try!
Yawn! Yell! Yodel! Yank!
```

### 🎵 Zigzag Zebra's Zee-Zee-Zee Song
```
Zee! Zee! Zee! Zigzag Zebra!
What can Zigzag Zebra do?
Zip! Zoom! Zigzag! Zonk!
Zigzag Zebra zaps too!

Zigzag Zebra zips the cage,
Zigzag Zebra zooms on stage,
Zigzag Zebra zigzags around,
Zigzag Zebra zonks — to the ground!

Zee! Zee! Zee! Now you try!
Zip! Zoom! Zigzag! Zonk!
```

## 統合バージョン（全26キャラ通し歌）

各キャラクター5行で26音すべてを1曲で通す。動詞は他動詞中心、簡単な日常語の目的語と組み合わせて「何をしているか」が一目でわかるように設計。オープニング／総集編／復習動画用。

### 🎵 Phonics Island ABC Song

```
[Intro]
Welcome, welcome, come along,
26 friends in one big song!
Wiggle, giggle, clap and shake,
Sing along — what fun we'll make!

Ay! Ay! Ay! Aunt Ant!
What can Aunt Ant do?
Aunt Ant asks a question,
Aunt Ant adds two apples,
Aunt Ant applauds — clap clap clap!

Bee! Bee! Bee! Baker Bear!
What can Baker Bear do?
Baker Bear bakes the bread,
Baker Bear blows a bubble,
Baker Bear builds it big and tall!

See! See! See! Cowboy Cat!
What can Cowboy Cat do?
Cowboy Cat catches a cow,
Cowboy Cat climbs the cliff,
Cowboy Cat counts to ten!

Dee! Dee! Dee! Doctor Dragon!
What can Doctor Dragon do?
Doctor Dragon draws a duck,
Doctor Dragon digs a hole,
Doctor Dragon dives — splash!

Ee! Ee! Ee! Engineer Egg!
What can Engineer Egg do?
Engineer Egg edits a book,
Engineer Egg enters a room,
Engineer Egg exercises — one, two, three!

Eff! Eff! Eff! Fisher Frog!
What can Fisher Frog do?
Fisher Frog finds a fly,
Fisher Frog flips a fish,
Fisher Frog flies a kite!

Gee! Gee! Gee! Guardian Goat!
What can Guardian Goat do?
Guardian Goat grows a flower,
Guardian Goat gives a gift,
Guardian Goat grabs a glove!

Aitch! Aitch! Aitch! Hiker Hippo!
What can Hiker Hippo do?
Hiker Hippo holds a hat,
Hiker Hippo hugs a friend,
Hiker Hippo hides — peek-a-boo!

Eye! Eye! Eye! Inventor Ice!
What can Inventor Ice do?
Inventor Ice invents a robot,
Inventor Ice imagines a star,
Inventor Ice imitates a cat — meow!

Jaye Jaye Jaye Juggler Jellyfish!
What can Juggler Jellyfish do?
Juggler Jellyfish juggles three balls,
Juggler Jellyfish jumps a rope,
Juggler Jellyfish joins the team!

Kay! Kay! Kay! King Kangaroo!
What can King Kangaroo do?
King Kangaroo kicks a ball,
King Kangaroo keeps a key,
King Kangaroo kisses his queen!

Ell! Ell! Ell! Librarian Lion!
What can Librarian Lion do?
Librarian Lion lifts a book,
Librarian Lion learns a letter,
Librarian Lion likes the library!

Em! Em! Em! Magician Mouse!
What can Magician Mouse do?
Magician Mouse makes a hat,
Magician Mouse mixes some milk,
Magician Mouse moves the mat!

En! En! En! Ninja Nut!
What can Ninja Nut do?
Ninja Nut nibbles a nut,
Ninja Nut names his pet,
Ninja Nut needs a nap!

Oh! Oh! Oh! Outlaw Octopus!
What can Outlaw Octopus do?
Outlaw Octopus opens an orange,
Outlaw Octopus offers a snack,
Outlaw Octopus orders an omelet!

P! P! P! Pilot Panda!
What can Pilot Panda do?
Pilot Panda paints a plane,
Pilot Panda pulls a rope,
Pilot Panda packs a parachute!

Cue! Cue! Cue! Queen Quiz!
What can Queen Quiz do?
Queen Quiz quizzes the class,
Queen Quiz questions a king,
Queen Quiz quacks like a duck!

Ar! Ar! Ar! Runner Rabbit!
What can Runner Rabbit do?
Runner Rabbit reads a book,
Runner Rabbit rolls a ball,
Runner Rabbit rides a bike!

Ess! Ess! Ess! Singer Snake!
What can Singer Snake do?
Singer Snake sings a song,
Singer Snake sees a star,
Singer Snake sips some soup!

Tee! Tee! Tee! Teacher Tacos!
What can Teacher Tacos do?
Teacher Tacos teaches a class,
Teacher Tacos taps a table,
Teacher Tacos throws a ball!

You! You! You! Uncle Unicorn!
What can Uncle Unicorn do?
Uncle Unicorn unzips a bag,
Uncle Unicorn unties a knot,
Uncle Unicorn unfolds a map!

Vee! Vee! Vee! Viking Virus!
What can Viking Virus do?
Viking Virus visits a friend,
Viking Virus vacuums the floor,
Viking Virus vanishes — poof!

Double-U! Double-U! Double-U! Waiter Wolf!
What can Waiter Wolf do?
Waiter Wolf washes a window,
Waiter Wolf waves his hand,
Waiter Wolf walks a dog!

Ex! Ex! Ex! Boxer Fox!
What can Boxer Fox do?
Boxer Fox fixes a clock,
Boxer Fox mixes the paint,
Boxer Fox waxes a car!

Why! Why! Why! Yoga Yeti!
What can Yoga Yeti do?
Yoga Yeti yells a word,
Yoga Yeti yanks a rope,
Yoga Yeti yawns — so sleepy!

Zee! Zee! Zee! Zigzag Zebra!
What can Zigzag Zebra do?
Zigzag Zebra zips a jacket,
Zigzag Zebra zooms around,
Zigzag Zebra zonks — to the ground!

[Outro]
A to Z, all 26,
Phonics Island friends — what a mix!
Hip hip hooray, jump and play,
We love English every day!
```

### 構造ノート
- 各キャラ5行：呼びかけ／問いかけ／行動文3つ（他動詞＋目的語）
- 行動文は日常語の目的語で動詞の意味が一目でわかるように
- 頭韻（同じアルファベットの目的語）は可能な範囲で活用：
  - 完全頭韻: Aunt Ant **a**pples / Baker Bear **b**read, **b**ubble / Outlaw Octopus **o**range, **o**melet など
  - 動作優先: catches a **cow**, draws a **duck**, mixes the **paint** など意味重視
- 5行目は擬音／オチで動作を強調し、次のキャラへバトン
- 26ブロック × 5行 + イントロ・アウトロ8行 = 計138行

### AI 生成時の補足
- Suno/Udio などに歌わせる場合、歌詞は上記の文字名スペル版（`Ay!` `Bee!` ...）をそのままコピー
- Style/Description 欄に補強指示：
  ```
  Children's phonics song, ABC alphabet song style.
  Pronounce all single-word letters as alphabet letter names
  (Ay = A, Bee = B, See = C, Dee = D, ...).
  Upbeat, friendly, kid-friendly vocals.
  ```
- W = "Double-U" は3音節で長いため、リズムに合わせて1拍に圧縮するか、`W` 単独表記に切り替えて Style 欄で "double-u" と明示する選択肢もある
- Z は米式 "Zee"。英国向けは "Zed" に置き換え

## 日本語訳バージョン（統合バージョンの対訳）

英語の統合バージョンと1行ずつ対応する日本語訳。動画字幕／指導者用リファレンス／日本語ナレーション動画用。

```
[イントロ]
ようこそ、ようこそ、こちらへどうぞ！
26人のなかまが ひとつのうたに！
ぴょんぴょん、にこにこ、てを たたこう
いっしょに うたって、たのしもう！

エイ！ エイ！ エイ！ アント・アント！
アント・アントは なにをする？
アント・アントは しつもんする、
アント・アントは リンゴを ふたつ たす、
アント・アントは てを たたく — パチパチパチ！

ビー！ ビー！ ビー！ ベイカー・ベア！
ベイカー・ベアは なにをする？
ベイカー・ベアは パンを やく、
ベイカー・ベアは シャボンだまを ふく、
ベイカー・ベアは おおきく たかく つくる！

スィー！ スィー！ スィー！ カウボーイ・キャット！
カウボーイ・キャットは なにをする？
カウボーイ・キャットは うしを つかまえる、
カウボーイ・キャットは がけを のぼる、
カウボーイ・キャットは 10まで かぞえる！

ディー！ ディー！ ディー！ ドクター・ドラゴン！
ドクター・ドラゴンは なにをする？
ドクター・ドラゴンは アヒルを かく、
ドクター・ドラゴンは あなを ほる、
ドクター・ドラゴンは とびこむ — ザブン！

イー！ イー！ イー！ エンジニア・エッグ！
エンジニア・エッグは なにをする？
エンジニア・エッグは ほんを なおす、
エンジニア・エッグは へやに はいる、
エンジニア・エッグは うんどうする — いち、にい、さん！

エフ！ エフ！ エフ！ フィッシャー・フロッグ！
フィッシャー・フロッグは なにをする？
フィッシャー・フロッグは ハエを みつける、
フィッシャー・フロッグは さかなを ひっくりかえす、
フィッシャー・フロッグは たこを とばす！

ジー！ ジー！ ジー！ ガーディアン・ゴート！
ガーディアン・ゴートは なにをする？
ガーディアン・ゴートは おはなを そだてる、
ガーディアン・ゴートは プレゼントを あげる、
ガーディアン・ゴートは てぶくろを つかむ！

エイチ！ エイチ！ エイチ！ ハイカー・ヒッポ！
ハイカー・ヒッポは なにをする？
ハイカー・ヒッポは ぼうしを もつ、
ハイカー・ヒッポは ともだちを ハグする、
ハイカー・ヒッポは かくれる — いない いない ばあ！

アイ！ アイ！ アイ！ インベンター・アイス！
インベンター・アイスは なにをする？
インベンター・アイスは ロボットを はつめいする、
インベンター・アイスは ほしを そうぞうする、
インベンター・アイスは ねこの まねをする — ニャー！

ジェイ！ ジェイ！ ジェイ！ ジャグラー・ジェリーフィッシュ！
ジャグラー・ジェリーフィッシュは なにをする？
ジャグラー・ジェリーフィッシュは ボールを 3つ ジャグリングする、
ジャグラー・ジェリーフィッシュは なわとびを とぶ、
ジャグラー・ジェリーフィッシュは チームに はいる！

ケイ！ ケイ！ ケイ！ キング・カンガルー！
キング・カンガルーは なにをする？
キング・カンガルーは ボールを ける、
キング・カンガルーは カギを もっている、
キング・カンガルーは おひめさまに キスする！

エル！ エル！ エル！ ライブラリアン・ライオン！
ライブラリアン・ライオンは なにをする？
ライブラリアン・ライオンは ほんを もちあげる、
ライブラリアン・ライオンは もじを まなぶ、
ライブラリアン・ライオンは としょかんが だいすき！

エム！ エム！ エム！ マジシャン・マウス！
マジシャン・マウスは なにをする？
マジシャン・マウスは ぼうしを つくる、
マジシャン・マウスは ぎゅうにゅうを まぜる、
マジシャン・マウスは マットを うごかす！

エヌ！ エヌ！ エヌ！ ニンジャ・ナット！
ニンジャ・ナットは なにをする？
ニンジャ・ナットは ナッツを かじる、
ニンジャ・ナットは ペットに なまえを つける、
ニンジャ・ナットは ひるねを する！

オウ！ オウ！ オウ！ アウトロー・オクトパス！
アウトロー・オクトパスは なにをする？
アウトロー・オクトパスは オレンジを ひらく、
アウトロー・オクトパスは おやつを すすめる、
アウトロー・オクトパスは オムレツを ちゅうもんする！

ピー！ ピー！ ピー！ パイロット・ピッグ！
パイロット・ピッグは なにをする？
パイロット・ピッグは ひこうきを ぬる、
パイロット・ピッグは ロープを ひっぱる、
パイロット・ピッグは パラシュートを つめる！

キュー！ キュー！ キュー！ クイーン・クイズ！
クイーン・クイズは なにをする？
クイーン・クイズは クラスに クイズをだす、
クイーン・クイズは おうじさまに しつもんする、
クイーン・クイズは アヒルみたいに ガーガーないて！

アー！ アー！ アー！ ランナー・ラビット！
ランナー・ラビットは なにをする？
ランナー・ラビットは ほんを よむ、
ランナー・ラビットは ボールを ころがす、
ランナー・ラビットは じてんしゃに のる！

エス！ エス！ エス！ シンガー・スネーク！
シンガー・スネークは なにをする？
シンガー・スネークは うたを うたう、
シンガー・スネークは ほしを みる、
シンガー・スネークは スープを すする！

ティー！ ティー！ ティー！ ティーチャー・タコス！
ティーチャー・タコスは なにをする？
ティーチャー・タコスは クラスを おしえる、
ティーチャー・タコスは つくえを たたく、
ティーチャー・タコスは ボールを なげる！

ユー！ ユー！ ユー！ アンクル・ユニコーン！
アンクル・ユニコーンは なにをする？
アンクル・ユニコーンは カバンの チャックを あける、
アンクル・ユニコーンは むすびめを ほどく、
アンクル・ユニコーンは ちずを ひろげる！

ヴィー！ ヴィー！ ヴィー！ バイキング・ウイルス！
バイキング・ウイルスは なにをする？
バイキング・ウイルスは ともだちを たずねる、
バイキング・ウイルスは ゆかを そうじする、
バイキング・ウイルスは きえる — ポフッ！

ダブリュー！ ダブリュー！ ダブリュー！ ウェイター・ウルフ！
ウェイター・ウルフは なにをする？
ウェイター・ウルフは まどを ふく、
ウェイター・ウルフは てを ふる、
ウェイター・ウルフは いぬを さんぽする！

エックス！ エックス！ エックス！ ボクサー・フォックス！
ボクサー・フォックスは なにをする？
ボクサー・フォックスは とけいを なおす、
ボクサー・フォックスは ペンキを まぜる、
ボクサー・フォックスは くるまを みがく！

ワイ！ ワイ！ ワイ！ ヨガ・イエティ！
ヨガ・イエティは なにをする？
ヨガ・イエティは ことばを さけぶ、
ヨガ・イエティは ロープを ひっぱる、
ヨガ・イエティは あくびする — ねむい〜！

ズィー！ ズィー！ ズィー！ ジグザグ・ゼブラ！
ジグザグ・ゼブラは なにをする？
ジグザグ・ゼブラは ジャケットの チャックを しめる、
ジグザグ・ゼブラは はしりまわる、
ジグザグ・ゼブラは バタンと たおれる — ドスン！

[アウトロ]
A から Z まで、ぜんぶで 26
フォニックスアイランドの なかまたち！
バンザイ バンザイ、ジャンプして あそぼう
まいにち えいごが だいすき！
```

### 翻訳ノート
- 文字名の読みは英語と同じカタカナ表記（エイ、ビー、スィー...）にすることで、英語版と1対1対応
- 動作の動詞は子どもになじみやすいやさしい言葉（やく、ぬる、つかむ等）を選択
- 擬音語（パチパチ、ザブン、ニャー、ポフッ、ドスン）で動きを強調
- 対応動画パターン：
  - パターンA: 英語で歌い、日本語字幕で意味を見せる
  - パターンB: 日本語版を BGM 的に挟んで意味を確認させる回
  - パターンC: 英語→日本語の交互ハーフバージョン

## 残タスク

- [x] 全26曲の歌詞作成
- [x] 統合バージョン（通し歌）作成
- [x] AI音楽生成用の文字名読みスペル版に変換
- [ ] 各キャラのビジュアルデザイン（衣装・色・体型）
- [ ] 動画スタイル決定（2Dアニメ／3D／パペット風など）
- [ ] index.html 入門編への組み込み設計
- [ ] 共通テーマソング（フォニックスアイランドのオープニング）
