from django.db import models


class Pitcher(models.Model):
    TEAM_CHOICES = [
        ("巨人", "読売ジャイアンツ"),
        ("阪神", "阪神タイガース"),
        ("広島", "広島東洋カープ"),
        ("中日", "中日ドラゴンズ"),
        ("DeNA", "横浜DeNAベイスターズ"),
        ("ヤクルト", "東京ヤクルトスワローズ"),
        ("ソフトバンク", "福岡ソフトバンクホークス"),
        ("ロッテ", "千葉ロッテマリーンズ"),
        ("西武", "埼玉西武ライオンズ"),
        ("楽天", "東北楽天ゴールデンイーグルス"),
        ("オリックス", "オリックス・バファローズ"),
        ("日本ハム", "北海道日本ハムファイターズ"),
    ]

    name = models.CharField(max_length=100, verbose_name="投手名")
    team = models.CharField(
        max_length=100, choices=TEAM_CHOICES, verbose_name="所属球団"
    )  # 自由入力か選択式かはお好みで
    innings_pitched = models.FloatField(default=0, verbose_name="投球回")
    earned_runs = models.IntegerField(default=0, verbose_name="自責点")
    wins = models.IntegerField(default=0, verbose_name="勝ち")
    losses = models.IntegerField(default=0, verbose_name="負け")
    holds = models.IntegerField(default=0, verbose_name="ホールド")
    saves = models.IntegerField(default=0, verbose_name="セーブ")

    def __str__(self):
        return self.name

    # 防御率を計算する機能（あとで追加・連携してもOK！）
    @property
    def era(self):
        if self.innings_pitched > 0:
            return round((self.earned_runs * 9) / self.innings_pitched, 2)
        return 0.00
    
    is_favorite = models.BooleanField(default=False, verbose_name="お気に入り")
    
    def add_performance(self, innings, earned_runs):
        """ 投球回を野球形式で加算するメソッド """
        # 現在のアウト数に変換 (例: 6.2 -> 6*3 + 2 = 20アウト)
        current_int = int(self.innings_pitched)
        current_frac = round((self.innings_pitched - current_int) * 10)
        total_outs = (current_int * 3) + current_frac
        
        # 加算するアウト数 (例: 0.2 -> 2アウト)
        new_int = int(innings)
        new_frac = round((innings - new_int) * 10)
        added_outs = (new_int * 3) + new_frac
        
        # 合計アウト数をイニングに戻す
        final_total_outs = total_outs + added_outs
        final_innings = (final_total_outs // 3) + (final_total_outs % 3 * 0.1)
        
        self.innings_pitched = final_innings
        self.earned_runs += earned_runs
        self.save()