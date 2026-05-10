from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Pitcher


# 1. ホーム画面
@login_required
def home(request):
    favorite_pitchers = Pitcher.objects.filter(is_favorite=True)
    return render(
        request, "players/home.html", {"favorite_pitchers": favorite_pitchers}
    )


# 2. 一覧 ＆ 登録画面
@login_required
def pitcher_list(request):
    sort_by = request.GET.get("sort", "name")
    team_filter = request.GET.get("team")

    # データを取得
    pitchers_queryset = Pitcher.objects.all()
    teams = Pitcher.TEAM_CHOICES  # これがドロップダウンの元データ

    # 球団で絞り込み
    if team_filter:
        pitchers_queryset = pitchers_queryset.filter(team=team_filter)

    # ソート処理
    if sort_by == "era":
        # 防御率はpropertyなのでPython側でソート
        pitchers = sorted(pitchers_queryset, key=lambda p: p.era)
    else:
        # DB側でソート
        pitchers = pitchers_queryset.order_by(sort_by)

    # 登録処理
    if request.method == "POST":
        ip = float(request.POST.get("innings_pitched") or 0)
        input_era = float(request.POST.get("input_era") or 0)
        # 防御率から自責点を逆算
        calculated_er = round((input_era * ip) / 9)

        Pitcher.objects.create(
            name=request.POST.get("name"),
            team=request.POST.get("team"),
            innings_pitched=ip,
            earned_runs=calculated_er,
            wins=int(request.POST.get("wins") or 0),
            losses=int(request.POST.get("losses") or 0),
            holds=int(request.POST.get("holds") or 0),
            saves=int(request.POST.get("saves") or 0),
        )
        return redirect("pitcher_list")

    # templateに渡す変数を整理
    context = {
        "pitchers": pitchers,
        "teams": teams,  # これがHTMLの {% for val, label in teams %} に対応
    }
    return render(request, "players/list.html", context)


# 3. 防御率計算ツール画面
@login_required
def calculator(request):
    query = request.GET.get("q")
    pitchers = (
        Pitcher.objects.filter(name__icontains=query)
        if query
        else Pitcher.objects.all()
    )

    if request.method == "POST":
        pitcher_id = request.POST.get("pitcher_id")
        if pitcher_id:
            pitcher = get_object_or_404(Pitcher, pk=pitcher_id)

            today_ip = float(request.POST.get("innings_pitched") or 0)
            today_er = int(request.POST.get("earned_runs") or 0)

            # イニング合算ロジック
            current_int = int(pitcher.innings_pitched)
            current_outs = (current_int * 3) + round(
                (pitcher.innings_pitched - current_int) * 10
            )

            added_int = int(today_ip)
            added_outs = (added_int * 3) + round((today_ip - added_int) * 10)

            total_outs = current_outs + added_outs
            pitcher.innings_pitched = (total_outs // 3) + (total_outs % 3 * 0.1)

            # 各種成績の加算
            pitcher.earned_runs += today_er
            pitcher.wins += int(request.POST.get("wins") or 0)
            pitcher.losses += int(request.POST.get("losses") or 0)
            pitcher.holds += int(request.POST.get("holds") or 0)
            pitcher.saves += int(request.POST.get("saves") or 0)

            pitcher.save()
            return redirect("pitcher_list")

    return render(
        request, "players/calculator.html", {"pitchers": pitchers, "query": query}
    )


# 4. 編集 ＆ お気に入り
@login_required
def pitcher_edit(request, pk):
    pitcher = get_object_or_404(Pitcher, pk=pk)
    if request.method == "POST":
        pitcher.name = request.POST.get("name")
        pitcher.team = request.POST.get("team")
        pitcher.innings_pitched = float(request.POST.get("innings_pitched") or 0)
        pitcher.earned_runs = int(request.POST.get("earned_runs") or 0)
        pitcher.wins = int(request.POST.get("wins") or 0)
        pitcher.losses = int(request.POST.get("losses") or 0)
        pitcher.holds = int(request.POST.get("holds") or 0)
        pitcher.saves = int(request.POST.get("saves") or 0)
        pitcher.save()
        return redirect("pitcher_list")

    return render(
        request,
        "players/edit.html",
        {"pitcher": pitcher, "teams": Pitcher.TEAM_CHOICES},
    )


@login_required
def toggle_favorite(request, pk):
    pitcher = get_object_or_404(Pitcher, pk=pk)
    pitcher.is_favorite = not pitcher.is_favorite
    pitcher.save()
    return redirect("pitcher_list")
