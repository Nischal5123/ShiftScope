// dataset fields
var movieFields = {
  categ: [
    "Creative_Type",
    "Director",
    "Distributor",
    "Major_Genre",
    "MPAA_Rating",
    "Source",
    "Title",
  ],
  date: ["Release_Date"],
  quant: [
    "IMDB_Rating",
    "IMDB_Votes",
    "Production_Budget",
    "Rotten_Tomatoes_Rating",
    "Running_Time_min",
    "US_DVD_Sales",
    "US_Gross",
    "Worldwide_Gross",
  ],
};

var bsFields = {
  categ: [
    "Aircraft_Airline_Operator",
    "Aircraft_Make_Model",
    "Airport_Name",
    "Effect_Amount_of_damage",
    "Origin_State",
    "When_Phase_of_flight",
    "When_Time_of_day",
    "Wildlife_Size",
    "Wildlife_Species",
  ],
  date: ["Flight_Date"],
  quant: ["Cost_Other", "Cost_Repair", "Cost_Total", "Speed_IAS_in_knots"],
};

// global vars
var bookmarkContent = document.querySelector(".bookmark_content");
var taskContent = document.querySelector("#task_content");
var fieldLst = document.querySelector(".attr-lst");

var mainImg = document.querySelector(".mainImg");
var relatedImg = document.querySelector(".relatedImg");

var rec = [];
var curRecLen = 0;

var checkedFields = [];
var propVglMap = {};
var propVglstrMap = {};
var bookmarked = {};

var curFields;

// window.href
var hrefSplit = window.location.href.split("/");
var hrefSplitLen = hrefSplit.length;
var status = hrefSplit[hrefSplitLen - 4];
var username = hrefSplit[hrefSplitLen - 3];
var version = hrefSplit[hrefSplitLen - 2];
var interface = hrefSplit[hrefSplitLen - 1];

//save cur answer
var curAns = "";

// interaction logs:
// {interaction: I1, time: T1}
// interaction type:
// open / close bookmark popup
// open / close task popup
// type in answer
//
var interactionLogs = [];
var scrollPos;

init();

function init() {
  initFields();
  initBtns();
  generateInitRecPlots();
  displayTask();
  storeInteractionLogs("study begins", "page loaded", new Date());
  if (interface === "p4") {
    setTimer(new Date());
  }
  scrollPos = document.querySelector(".page_content").scrollTop;

  // adding scroll event
  document
    .querySelector(".page_content")
    .addEventListener("scroll", function () {
      // detects new state and compares it with the new one
      // console.log(scrollPos, document.querySelector(".page_content").scrollTop);
      if (document.querySelector(".page_content").scrollTop > scrollPos) {
        // console.log("scroll up.");
        storeInteractionLogs("scroll down", "", new Date());
      } else {
        // console.log("scroll down.");
        storeInteractionLogs("scroll up", "", new Date());
      }
      // saves the new position for iteration.
      scrollPos = document.querySelector(".page_content").scrollTop;
    });
}

function setTimer(oldDate) {
  let countDownDate = new Date(oldDate.getTime() + 15 * 60000 + 10 * 1000);
  var x = setInterval(function () {
    // Get today's date and time
    var now = new Date().getTime();

    // Find the distance between now and the count down date
    var distance = countDownDate - now;

    // Time calculations for days, hours, minutes and seconds
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Output the result in an element with id="demo"
    document.getElementById("timer").innerHTML =
      "Count Down: " + minutes + "m " + seconds + "s ";

    // If the count down is over, write some text
    if (distance < 0) {
      clearInterval(x);
      document.getElementById("timer").innerHTML = "Time is up.";
      document.getElementById("timer").style.color = "red";
      alert(
        "15 mins is up. You should submit your answer and then go to the next step."
      );
    }
  }, 1000);
}

function initBtns() {
  let bmModal = document.querySelector("#bmpopup");
  let bmBtn = document.querySelector("#bookmark");
  let bmClose = document.querySelector("#bmclose");
  let bmBtn2 = document.querySelector("#check-bookmark");

  bmBtn.addEventListener("click", () => {
    if (bmModal.style.display == "block") {
      bmModal.style.display = "none";
      storeInteractionLogs("closed window", "bookmark popup", new Date());
    } else {
      bmModal.style.display = "block";
      refreshBookmark();
      storeInteractionLogs("opened window", "bookmark popup", new Date());
    }
  });
  bmBtn2.addEventListener("click", () => {
    if (bmModal.style.display == "block") {
      bmModal.style.display = "none";
      storeInteractionLogs("closed window", "check bookmarks", new Date());
    } else {
      bmModal.style.display = "block";
      refreshBookmark();
      storeInteractionLogs("opened window", "check bookmarks", new Date());
    }
  });

  bmClose.addEventListener("click", () => {
    bmModal.style.display = "none";
    storeInteractionLogs("closed window", "bookmark popup", new Date());
  });

  window.addEventListener("click", (event) => {
    if (event.target == bmModal) {
      bmModal.style.display = "none";
      storeInteractionLogs("closed window", "bookmark popup", new Date());
    }
  });

  let ptaskIds = [
    "confidence-udata",
    "confidence-ans",
    "efficiency",
    "ease-of-use",
    "utility",
    "overall",
  ];

  for (let ptid of ptaskIds) {
    document.getElementById(ptid).addEventListener("change", () => {
      storeInteractionLogs(
        "changed ptask ans of " + ptid,
        document.getElementById(ptid).value,
        new Date()
      );
    });
  }
}

function initFields() {
  fieldLst.innerHTML = "";
  let res = "";
  let url_break = window.location.href.split("/");
  let version = url_break[url_break.length - 2];
  if (version[0] === "a") {
    curFields = movieFields;
  } else {
    curFields = bsFields;
  }
  for (e of curFields.categ) {
    res += `<li class="categ-attr enabled">
                    <div>
                        <i class="fas fa-font"></i> &nbsp;
                        <label class="form-check-label" for="${e}">
                           ${e}
                        </label>
                        <span class="check float-right">
                            <input class="form-check-input" type="checkbox" value="${e}" id="${e}"/>
                        </span>
                    </div>
                </li>`;
  }
  for (e of curFields.date) {
    res += `<li class="date-attr enabled">
                    <div>
                        <i class="fas fa-calendar-alt"></i> &nbsp;
                        <label class="form-check-label" for="${e}"> ${e} </label>
                        <span class="check float-right">
                            <input class="form-check-input" type="checkbox" value="${e}" id="${e}" />
                        </span>
                    </div>
                </li>`;
  }
  for (e of curFields.quant) {
    res += `<li class="quant-attr enabled">
                    <div>
                        <i class="fas fa-hashtag"></i> &nbsp;
                        <label class="form-check-label" for="${e}"> ${e} </label>
                        <span class="check float-right">
                            <input class="form-check-input" type="checkbox" value="${e}" id="${e}" />
                        </span>
                    </div>
                </li>`;
  }
  fieldLst.innerHTML += res;
  // add click on fields event
  let fldCheckboxes = document.querySelectorAll("form .enabled div");
  for (fldcb of fldCheckboxes) {
    fldcb.addEventListener("click", clickOnField);
  }

  // make sure all boxes are unchecked
  let all_boxes = document.querySelectorAll(".form-check-input");
  for (box of all_boxes) {
    box.checked = false;
  }
}

function clickOnField(e) {
  let box = e.target;
  if (box != null) {
    let clickedField = box.value;
    // if a box is checked after the click
    if (box.checked) {
      // if we can check more fields add the field in.
      // also add its parsed name to the list.
      if (checkedFields.length < 3) {
        checkedFields.push(clickedField);
        storeInteractionLogs(
          "clicked on a field",
          "add " + clickedField,
          new Date()
        );
        // if we can not check more fields, alert it.
      } else {
        storeInteractionLogs(
          "clicked on a field",
          "tried to add " +
            clickedField +
            ", but failed because already selected 3 fields",
          new Date()
        );
        alert(`You have selected more than 3 fields!`);
        box.checked = false;
        return;
      }

      // if a box is unchecked after the click,
      // also remove its parsed name from the list.
    } else {
      storeInteractionLogs(
        "clicked on a field",
        "remove " + clickedField,
        new Date()
      );
      checkedFields = checkedFields.filter(function (value, index, arr) {
        return value.localeCompare(clickedField) != 0;
      });
      // if 0 fields are checked, display alternative message.
      if (checkedFields.length == 0) {
        generateInitRecPlots();
        return;
      }
    }
    generatePlot(clickedField, box);
  }
}

function generateInitRecPlots() {
  var data = {
    data: JSON.stringify({
      fields: [],
      version: version,
    }),
  };
  $.ajax({
    async: false,
    type: "POST",
    url: "/perform_snd_flds",
    currentType: "application/json",
    data: data,
    dataType: "json",
    success: function (response) {
      console.log(response);
      mainImg.innerHTML = `No specified visualization yet. Start exploring by selecting fields on the Field panel or specifying a chart below.`;
      relatedImg.innerHTML = "";
      rec = response.recVegalite;
      for (var i = 0; i < rec.length; i++) {
        for (let prop in rec[i]) {
          let prop_str = JSON.stringify(prop).replace(/\W/g, "");
          let vglSpec = rec[i][prop];
          let sFlds = getFieldsFromVgl(vglSpec);
          let added_str = "";
          for (let fld of sFlds) {
            if (curFields.categ.includes(fld)) {
              added_str += `<i class="fas fa-font show_fld"> ${fld} </i>`;
            }
            if (curFields.quant.includes(fld)) {
              added_str += `<i class="fas fa-hashtag show_fld"> ${fld} </i>`;
            }
            if (curFields.date.includes(fld)) {
              added_str += `<i class="fas fa-calendar-alt show_fld"> ${fld} </i>`;
            }
            // console.log(added_str);
          }
          relatedImg.innerHTML += `<div class='view_wrapper ${prop_str}_wrapper'> ${added_str} <i class='fas fa-bookmark add_bm' added="false"></i><i class="fas fa-list-alt specify_chart"></i><div class="views" id='${prop_str}'></div></div>`;

          vegaEmbed(`#${prop_str}`, vglSpec, { actions: false });
          propVglMap[prop_str] = vglSpec;
          propVglstrMap[prop_str] = prop;
        }
      }
      document.querySelector(".loadmoreDiv").style.display = "none";
      addChartBtnsListener();
      addChartsListener();
    },
  });
}

function generatePlot(clickedField, box) {
  console.log(checkedFields);
  var data = {
    data: JSON.stringify({
      fields: checkedFields,
      version: version,
    }),
  };
  $.ajax({
    async: false,
    type: "POST",
    url: "/perform_snd_flds",
    currentType: "application/json",
    data: data,
    dataType: "json",
    success: function (response) {
      if (response.status === "success") {
        console.log(response);
        var vglDict = response.actualVegalite;
        rec = response.recVegalite;
        for (let prop in vglDict) {
          prop_str = prop.replace(/\W/g, "");
          let added_str = "";
          checkedFields.sort();
          for (let fld of checkedFields) {
            if (curFields.categ.includes(fld)) {
              added_str += `<i class="fas fa-font show_fld"> ${fld} </i>`;
            }
            if (curFields.quant.includes(fld)) {
              added_str += `<i class="fas fa-hashtag show_fld"> ${fld} </i>`;
            }
            if (curFields.date.includes(fld)) {
              added_str += `<i class="fas fa-calendar-alt show_fld"> ${fld} </i>`;
            }
            console.log(added_str);
          }
          mainImg.innerHTML = `<div id="main_wrapper" class="view_wrapper ${prop_str}_wrapper"> ${added_str} <i class="fas fa-bookmark add_bm" added="false"></i><div class="views ${prop_str}" id="main"></div></div>`;
          let vglSpec = vglDict[prop];
          vegaEmbed("#main", vglSpec, { actions: false });
          propVglMap[prop_str] = vglSpec;
          propVglstrMap[prop_str] = prop;

          storeInteractionLogs(
            "main chart changed because of clicking a field",
            prop,
            new Date()
          );
        }
        generateRecPlots();
      } else if (response.status === "empty") {
        storeInteractionLogs(
          "triggered empty chart",
          "remove " + clickedField,
          new Date()
        );
        // if empty chart
        alert(
          "Sorry, we cannot generate charts with the combination of selected fields."
        );
        checkedFields = checkedFields.filter(function (value, index, arr) {
          return value.localeCompare(clickedField) != 0;
        });
        box.checked = false;
      }
    },
  });
}

function generateRecPlots() {
  relatedImg.innerHTML = "";
  document.querySelector(".loadmoreDiv").style.display = "none";
  console.log(rec);
  let maxNum = 5;
  if (maxNum > rec.length) {
    maxNum = rec.length;
  }
  for (var i = 0; i < rec.length; i++) {
    for (let prop in rec[i]) {
      let prop_str = JSON.stringify(prop).replace(/\W/g, "");

      let vglSpec = rec[i][prop];

      let sFields = getFieldsFromVgl(vglSpec);
      // console.log(sFields);
      let added_str = "";
      for (let fld of sFields) {
        if (curFields.categ.includes(fld)) {
          added_str += `<i class="fas fa-font show_fld"> ${fld} </i>`;
        }
        if (curFields.quant.includes(fld)) {
          added_str += `<i class="fas fa-hashtag show_fld"> ${fld} </i>`;
        }
        if (curFields.date.includes(fld)) {
          added_str += `<i class="fas fa-calendar-alt show_fld"> ${fld} </i>`;
        }
      }

      relatedImg.innerHTML += `<div class='view_wrapper ${prop_str}_wrapper'> ${added_str} <i class='fas fa-bookmark add_bm' added="false"></i><i class="fas fa-list-alt specify_chart"></i><div class="views" id='${prop_str}'></div></div>`;
      vegaEmbed(`#${prop_str}`, vglSpec, { actions: false });

      propVglMap[prop_str] = vglSpec;
      propVglstrMap[prop_str] = prop;
      if (i >= maxNum) {
        document.querySelector(`.${prop_str}_wrapper`).style.display = "none";
      }
    }
  }
  addChartBtnsListener();
  addChartsListener();

  if (rec.length > 5) {
    curRecLen = 5;
    document.querySelector(".loadmoreDiv").style.display = "block";
    document
      .querySelector("#loadmoreBtn")
      .addEventListener("click", loadMoreRec);
  }
}

function loadMoreRec() {
  storeInteractionLogs("clicked load more button", "", new Date());
  let maxNum = curRecLen + 5;
  if (maxNum >= rec.length) {
    maxNum = rec.length;
    document.querySelector(".loadmoreDiv").style.display = "none";
  }
  for (var i = curRecLen; i < maxNum; i++) {
    for (let prop in rec[i]) {
      let prop_str = JSON.stringify(prop).replace(/\W/g, "");
      console.log(`${prop_str}_wrapper`);
      document.querySelector(`.${prop_str}_wrapper`).style.display = "block";
    }
  }
  curRecLen = maxNum;
}

function specifyChart(e) {
  let vis = e.target.parentElement;
  let prop_str = vis.classList.item(1).split("_wrapper")[0];
  let vglSpec = propVglMap[prop_str];

  storeInteractionLogs("specified chart", propVglstrMap[prop_str], new Date());

  reassignFields(vglSpec);

  var data = {
    data: JSON.stringify({
      vgl: vglSpec,
      version: version,
    }),
  };
  $.ajax({
    async: false,
    type: "POST",
    url: "/perform_snd_spcs",
    currentType: "application/json",
    data: data,
    dataType: "json",
    success: function (response) {
      console.log(response);
      rec = response.recVegalite;

      let sFields = getFieldsFromVgl(vglSpec);
      console.log(sFields);
      let added_str = "";
      for (let fld of sFields) {
        if (curFields.categ.includes(fld)) {
          added_str += `<i class="fas fa-font show_fld"> ${fld} </i>`;
        }
        if (curFields.quant.includes(fld)) {
          added_str += `<i class="fas fa-hashtag show_fld"> ${fld} </i>`;
        }
        if (curFields.date.includes(fld)) {
          added_str += `<i class="fas fa-calendar-alt show_fld"> ${fld} </i>`;
        }
      }

      mainImg.innerHTML = `<div id="main_wrapper" class="view_wrapper ${prop_str}_wrapper"> ${added_str} <i class="fas fa-bookmark add_bm" added="false"></i><div class="views ${prop_str}" id="main"></div></div>`;

      vegaEmbed("#main", vglSpec, { actions: false });
      generateRecPlots();
    },
  });
}

function reassignFields(vgljson) {
  console.log(vgljson);
  let all_boxes = document.querySelectorAll(".form-check-input");
  // console.log(all_boxes);

  let fields = getFieldsFromVgl(vgljson);

  for (box of all_boxes) {
    // console.log(box.value);
    if (fields.includes(box.value)) {
      box.checked = true;
    } else {
      box.checked = false;
    }
  }
  checkedFields = fields;
}

function addChartBtnsListener() {
  // add event listeners to all bookmark buttons on the page
  let btns = document.querySelectorAll(".add_bm");
  for (btn of btns) {
    btn.addEventListener("click", toggleBookMark);
  }

  let specBtns = document.querySelectorAll(".specify_chart");
  for (sBtn of specBtns) {
    sBtn.addEventListener("click", specifyChart);
  }

  let wrappers = document.querySelectorAll(".view_wrapper");

  // change color and state of a bookmark if a wrapper is in the bookmark content.
  for (wrapper of wrappers) {
    let item = `${wrapper.classList.item(1).split("_wrapper")[0]}`;
    if (item in bookmarked) {
      wrapper.querySelector(".add_bm").style.color = "#ffa500";
      wrapper.querySelector(".add_bm").setAttribute("added", "true");
    }
  }
}

function toggleBookMark(e) {
  let btn = e.target;
  let vis = e.target.parentElement;
  let str = vis.classList.item(1);
  // if the mark was checked, user want to uncheck it.
  if (btn.getAttribute("added") == "true") {
    // remove bookmark from pop up window
    let arr = bookmarkContent.childNodes;
    for (n of arr) {
      if (
        `${str}`
          .split("_wrapper")[0]
          .split("_bm")[0]
          .localeCompare(n.classList.item(1).split("_bm")[0]) == 0
      ) {
        bookmarkContent.removeChild(n);
      }
    }
    let splittedStr = `${str.split("_wrapper")[0]}`;
    delete bookmarked[splittedStr];
    storeInteractionLogs(
      "deleted chart from bookmark",
      propVglstrMap[splittedStr],
      new Date()
    );

    // change color and state of the plot in views
    let mark = document.querySelector(`.${str.split("_bm")[0]} .add_bm`);
    if (mark != null) {
      mark.style.color = "rgb(216, 212, 223)";
      mark.setAttribute("added", "false");
    }
    refreshBookmark();

    // if the mark is unchecked, user want to check it.
  } else {
    btn.style.color = "#ffa500";
    btn.setAttribute("added", "true");

    let splittedStr = `${str.split("_wrapper")[0]}`;

    bookmarked[splittedStr] = propVglMap[splittedStr];

    storeInteractionLogs(
      "added chart to bookmark",
      propVglstrMap[splittedStr],
      new Date()
    );
    refreshBookmark();
  }
}

function refreshBookmark() {
  let btnstrs = [];

  if (Object.keys(bookmarked).length == 0) {
    bookmarkContent.innerHTML =
      "Oops, you don't have any bookmark yet. Click on bookmark tags on charts to add a bookmark!";
  } else {
    bookmarkContent.innerHTML = "";
    for (key of Object.keys(bookmarked)) {
      let value = bookmarked[key];
      console.log(bookmarked);
      console.log(key);

      let sFields = getFieldsFromVgl(propVglMap[key]);
      console.log(sFields);
      let added_str = "";
      for (let fld of sFields) {
        if (curFields.categ.includes(fld)) {
          added_str += `<i class="fas fa-font show_fld"> ${fld} </i>`;
        }
        if (curFields.quant.includes(fld)) {
          added_str += `<i class="fas fa-hashtag show_fld"> ${fld} </i>`;
        }
        if (curFields.date.includes(fld)) {
          added_str += `<i class="fas fa-calendar-alt show_fld"> ${fld} </i>`;
        }
      }

      // creat div structure append to the popup window.
      bookmarkContent.innerHTML += `<div class="view_wrapper ${key}_wrapper_bm" > ${added_str} <i class="fas fa-bookmark add_bm" added="true"></i><div class="views" id="${key}_bm"></div></div>`;

      // plot the recommandation
      vegaEmbed(`#${key}_bm`, value, { actions: false });

      btnstrs.push(`.${key}_wrapper_bm .add_bm`);
      let btn = document.querySelector(`.${key}_wrapper_bm .add_bm`);

      // change color and attribute of bookmark.
      btn.style.color = "#ffa500";
      btn.setAttribute("added", "true");
    }
    // add event listener to new bookmark
    for (btn of btnstrs)
      document.querySelector(btn).addEventListener("click", toggleBookMark);
  }
}

function displayTask() {
  if (version[0] === "a" && interface[1] === "1") {
    taskContent.innerHTML =
      "<div><b>Question:</b> Which creative type has the maximum number of movies based on Book/Short Story (Source)?<br> Please <b>enter your answer</b> and also <b>bookmark charts</b> you think that could answer the question. <br><br><label>Your answer:</label> &nbsp;&nbsp; <select name='t1-answer' id='t1-answer'><option value=''></option><option value='contemporary_fiction'>Contemporary Fiction</option><option value='dramatization'>Dramatization</option><option value='factual'>Factual</option><option value='fantasy'>Fantasy</option><option value='historical_fiction'>Historical Fiction</option><option value='kids_fiction'>Kids Fiction</option><option value='multiple_creative_types'>Multiple Creative Types</option><option value='science_fiction'>Science Fiction</option><option value='super_hero'>Super Hero</option><option value='null'>null</option></select><br><br></div>";
  } else if (version[0] === "a" && interface[1] === "2") {
    taskContent.innerHTML =
      "<div><b>Question:</b> Among Disney Ride (Source) movies, what is the running time (mins) of the highest Worldwide grossing movie? <br> Please <b>enter your answer</b> and also <b>bookmark charts</b> you think that could answer the question. <br><br><label>Your answer:</label> &nbsp;&nbsp;<textarea id='t2-answer' rows='1' cols='34'></textarea><br><br></div>";
  } else if (version[0] === "a" && interface[1] === "3") {
    taskContent.innerHTML =
      "<div><b>Question:</b> What kinds of movies will be the most successful movies based on your observations of the data? Summarize the 2-3 characteristics that you believe are most important in predicting their success.<br>  Please <b>enter your answer</b> and also <b>bookmark at least 5 charts</b> you think that could demostrate or highlight your thoughts. <br><br><label>Your answer:</label> &nbsp;&nbsp; <textarea id='t3-answer' rows='10' cols='34'></textarea><br> <input type='checkbox' id='t3-complete-bm' /> &nbsp;&nbsp; <label>I have also bookmarked the charts which I think they could answer the quesion.</label><br><br></div>";
  } else if (version[0] === "b" && interface[1] === "1") {
    taskContent.innerHTML =
      "<div><b>Question:</b> When phase of flight has the highest number of birdstrike records in June (Flight_Date)?<br> Please <b>enter your answer</b> and also <b>bookmark charts</b> you think that could answer the question. <br><br><label>Your answer:</label> &nbsp;&nbsp; <select name='t1-answer' id='t1-answer'><option value=''></option><option value='approach'>Approach</option><option value='climb'>Climb</option><option value='descent'>Descent</option><option value='landing_roll'>Landing Roll</option><option value='parked'>Parked</option><option value='take-off_run'>Take-off run</option><option value='taxi'>Taxi</option></select><br><br></div>";
  } else if (version[0] === "b" && interface[1] === "2") {
    taskContent.innerHTML =
      "<div><b>Question:</b> What speed (IAS) in knots could cause the substantial (Effect Amount of damage) damage of AVRO RJ 85 (Aircraft Make Model)? <br> Please <b>enter your answer</b> and also <b>bookmark charts</b> you think that could answer the question. <br><br><label>Your answer:</label> &nbsp;&nbsp;<textarea id='t2-answer' rows='1' cols='34'></textarea><br><br></div>";
  } else if (version[0] === "b" && interface[1] === "3") {
    taskContent.innerHTML =
      "<div><b>Question:</b> What kinds of birdstrikes would usually cost the most to repair the airplane? Note that any dataset columns that are interesting to you can be included. Summarize the 2-3 factors that you believe would cause the highest repair cost.<br>  Please <b>enter your answer</b> and also <b>bookmark at least 5 charts</b> you think that could demostrate or highlight your thoughts. <br><br><label>Your answer:</label> &nbsp;&nbsp; <textarea id='t3-answer' rows='10' cols='34'></textarea><br><br></div>";
  } else if (interface[1] === "4") {
    taskContent.innerHTML =
      "<div><b>Question:</b> Feel free to explore any and all aspects of the data for up to <b>[15 mins]</b>. Use the bookmark features to save any interesting patterns, trends or other insights worth sharing with colleagues. Note the top 5 bookmarks that you found most interesting from your exploration.<br> Please <b>write down your insights</b> and also <b>bookmark top 5 charts</b> you think that could answer the question. <br><br> <label>Your insights:</label> &nbsp;&nbsp; <textarea id='t4-answer' rows='10' cols='34'></textarea><br><br></div>";
  }
  let ansId = "t" + interface[1] + "-answer";
  document.getElementById(ansId).addEventListener("input", function () {
    storeInteractionLogs(
      "typed in answer",
      document.getElementById(ansId).value,
      new Date()
    );
  });
}

function goStopPage() {
  storeInteractionLogs("hit the submit button", "", new Date());

  // check answer
  let ansId = "t" + interface[1] + "-answer";
  let answer = document.getElementById(ansId).value;

  if (answer === "") {
    storeInteractionLogs(
      "submission failed",
      "the answer is empty",
      new Date()
    );
    alert("Please answer the question.");
    return;
  }

  // check if bookmarked list empty or not
  if (interface[1] == 3) {
    if (Object.keys(bookmarked).length < 5) {
      alert("Please bookmark at least 5 charts for this task.");
      storeInteractionLogs(
        "submission failed",
        "did not bookmark the correct number of charts",
        new Date()
      );
      return;
    }
  } else if (interface[1] == 4) {
    if (Object.keys(bookmarked).length != 5) {
      alert("You could only bookmark 5 charts for this task.");
      storeInteractionLogs(
        "submission failed",
        "did not bookmark the correct number of charts",
        new Date()
      );
      return;
    }
  } else {
    if (Object.keys(bookmarked).length == 0) {
      alert(
        "Please bookmark charts that you think they could answer the question."
      );
      storeInteractionLogs(
        "submission failed",
        "did not bookmark charts",
        new Date()
      );
      return;
    }
  }

  // check post task questionnaire
  let ptaskIds = [
    "confidence-udata",
    "confidence-ans",
    "efficiency",
    "ease-of-use",
    "utility",
    "overall",
  ];

  for (let ptid of ptaskIds) {
    if (document.getElementById(ptid).value === "") {
      alert("Please complete the post-task questionnaire.");
      storeInteractionLogs(
        "submission failed",
        "did not complete the post-task questionnaire",
        new Date()
      );
      return;
    }
  }

  let ptaskAns = {};
  for (let ptid of ptaskIds) {
    ptaskAns[ptid] = document.getElementById(ptid).value;
  }

  storeInteractionLogs("submitted successfully", "", new Date());
  //send all data back to server
  var data = {
    data: JSON.stringify({
      interactionLogs: interactionLogs,
      status: status,
      username: username,
      version: version,
      interface: interface,
      answer: answer,
      bookmarked: bookmarked,
      ptaskAns: ptaskAns,
    }),
  };
  $.ajax({
    async: false,
    type: "POST",
    url: "/snd_interaction_logs",
    currentType: "application/json",
    data: data,
    dataType: "json",
    success: function (response) {
      console.log(response);
    },
  });
  window.location =
    "/" + status + "/" + username + "/" + version + "/s" + interface[1];
}

function addChartsListener() {
  allCharts = document.getElementsByClassName("views");
  // console.log(allCharts);
  for (let chart of allCharts) {
    // console.log(chart);
    if (chart.id !== "main") {
      chart.addEventListener("scroll", () => {
        storeInteractionLogs(
          "scroll on a related chart",
          propVglstrMap[chart.id],
          new Date()
        );
      });
      chart.addEventListener("mouseover", () => {
        storeInteractionLogs(
          "mouseover a related chart",
          propVglstrMap[chart.id],
          new Date()
        );
      });
      chart.addEventListener("mouseout", () => {
        storeInteractionLogs(
          "mouseout a related chart",
          propVglstrMap[chart.id],
          new Date()
        );
      });
    } else {
      let chartID = chart.className.split(" ")[1];
      chart.addEventListener("scroll", () => {
        storeInteractionLogs(
          "scroll on the specified chart",
          propVglstrMap[chartID],
          new Date()
        );
      });
      chart.addEventListener("mouseover", () => {
        storeInteractionLogs(
          "mouseover on the specified chart",
          propVglstrMap[chartID],
          new Date()
        );
      });
      chart.addEventListener("mouseout", () => {
        storeInteractionLogs(
          "mouseout on the specified chart",
          propVglstrMap[chartID],
          new Date()
        );
      });
    }
  }
}

function storeInteractionLogs(interaction, value, time) {
  console.log({ Interaction: interaction, Value: value, Time: time.getTime() });
  interactionLogs.push({
    Interaction: interaction,
    Value: value,
    Time: time.getTime(),
  });
}

function getFieldsFromVgl(vgl) {
  var flds = [];
  for (encode in vgl["encoding"]) {
    if ("field" in vgl["encoding"][encode]) {
      flds.push(vgl["encoding"][encode]["field"]);
    }
  }
  flds.sort();
  return flds;
}
