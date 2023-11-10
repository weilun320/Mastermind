$(document).ready(function() {

    // Only executes when path is "/"
    if($(location).attr("pathname") === "/") {
        // Colors array for setting question pins
        const colors = ["blue", "orange", "green", "red", "purple", "white", "yellow", "black"];
        // To remember which color pin user has dragged
        var colorPin;
        var checkCounter = 0, counter = 0, pinCounter = 0;

        // Gets number of pins
        var pinNumber = getPinNumber();
        // Sets question pins
        var question = randomizeQuestion(pinNumber, getDuplication());

        // Sets number of pins
        setPin(pinNumber);

        // Auto scroll to game section when page is load
        $("html, body").scrollTop($("#game").offset().top);

        $(window).on("beforeunload", function() {
            // Ask user for confirm leaving page
            return "";
        });

        let color = $(".colors");
        // Set each color pins with dragstart and dragend event
        color.each(function(n) {
            // Start dragging
            $(this).on("dragstart", function() {
                $(this).css("opacity", "0.4");

                // Get color pin class
                let pin = $(this).attr("class").split(/\s+/);

                // Ensure color's class existed in array
                for (var i = 0; i < pin.length; i++) {
                    if ($.inArray(pin[i], colors) > -1) {
                        colorPin = pin[i];
                    } else {
                        colorPin = String(colors[n]);
                        $(this).addClass(String(colors[n]));
                    }
                }
            });
            // End dragging
            $(this).on("dragend", function() {
                $(this).css("opacity", "1");
            });
        });

        let answers = $(".answer");
        // Set each answer pins with dragover, dragenter, dragleave, drop event
        answers.each(function() {
            // Draggable item over
            $(this).on("dragover", function(e) {
                // Prevent event happened by default
                e.preventDefault();
                return false;
            });
            // Draggable item enter
            $(this).on("dragenter", function() {
                if ($(this).hasClass("answer")) {
                    $(this).addClass("dragover");

                    let pin = $(this).attr("class").split(/\s+/);

                    // Remove any color pin when another color pin enter
                    for (var i = 0; i < pin.length; i++) {
                        if ($.inArray(pin[i], colors) > -1) {
                            $(this).removeClass(pin[i]);
                        }
                    }
                }
            });
            // Draggable item leave
            $(this).on("dragleave", function() {
                if ($(this).hasClass("answer")) {
                    $(this).removeClass("dragover");
                    checkColors();
                }
            });
            // Draggable item drop
            $(this).on("drop", function(e) {
                // Prevent propagation to siblings element
                e.stopPropagation();

                if ($(this).hasClass("answer")) {
                    $(this).removeClass("dragover");
                    // Set color pin's class to answer pin
                    $(this).addClass(colorPin);
                    checkColors();
                }

                return false;
            });
        });

        // Check button clicked
        $("#btnCheck").click(function() {
            // Get submitted answer
            let answer = getAnswer();

            // Ensure answer is same as number of pin
            if (answer.length != pinNumber) {
                $("#btnCheck").attr("disabled", true);
            } else {
                // Check for correct color and position and/or correct color pin
                let correctPin = checkCorrectPin(question, answer);
                let correctColor = checkCorrectColor(question, answer, correctPin);
                var checkPin = $(".pin-check").children();

                // Set small pin for correct color and position and/or correct color pin
                setCorrectPin(checkPin, correctPin);
                setCorrectColor(checkPin, correctColor);
                setChecked(checkPin, pinNumber);

                // Calculate number of correct color and position pin
                for (var i = 0; i < checkCounter; i++) {
                    if (checkPin.eq(i).hasClass("correct-pin")) {
                        pinCounter++;
                    }
                }

                // User wins if number of correct color and position pin same as number of pin
                if (pinCounter == pinNumber) {
                    // Disable check button
                    $("#btnCheck").attr("disabled", true);
                    // Trigger click on modal button
                    $("#btnModal").trigger("click");
                    // Remove before unload event
                    $(window).off("beforeunload");

                    // Reveal color at question pins
                    for (var i = 0; i < question.length; i++) {
                        var questionPin = $(".pin-question").children();
                        if (questionPin.eq(i).hasClass("question")) {
                            questionPin.eq(i).addClass(question[i]);
                            questionPin.eq(i).removeClass("question");
                            questionPin.eq(i).empty();
                        }
                    }

                    // Remove all event of color pins
                    let color = $(".colors");
                    color.each(function() {
                        $(this).off();
                    });

                    // Remove all event of answer pins
                    let answers = $(".answer");
                    answers.each(function() {
                        $(this).off();
                    });
                } else {
                    // Get number of rows guessed
                    var rows = $("#rows").children().length;
                    // The game continues if row guessed less than 10
                    if (rows < 10) {
                        if ($(".pin-answer").children().hasClass("answer")) {
                            $(".pin-answer").children().removeClass("answer");
                        }

                        // Clone the answer pins to be inserted to next row
                        let clone = $("#pin-row").clone(true);
                        clone.children(".pin-answer").children().removeClass().addClass("circle answer");
                        clone.children(".pin-check").children().removeClass().addClass("check");
                        clone.children(".btn-container").children().attr("disabled", true);
                        clone.children(".row-number").text(parseInt($("#pin-row").children(".row-number").text()) + 1);
                        // Insert cloned row above the previous row
                        clone.insertBefore("#pin-row");
                        // Remove previous check button
                        $(".check-btn").last().remove();
                        // Reset all counter
                        counter = 0;
                        checkCounter = 0;
                        pinCounter = 0;
                    } else {
                        // Disable check button
                        $("#btnCheck").attr("disabled", true);
                        // Trigger click on modal button
                        $("#btnModal").trigger("click");
                        // Remove before unload event
                        $(window).off("beforeunload");

                        // Reveal color at question pins
                        for (var i = 0; i < question.length; i++) {
                            var questionPin = $(".pin-question").children();
                            if (questionPin.eq(i).hasClass("question")) {
                                questionPin.eq(i).addClass(question[i]);
                                questionPin.eq(i).removeClass("question");
                                questionPin.eq(i).empty();
                            }
                        }

                        // Remove all event of color pins
                        let color = $(".colors");
                        color.each(function() {
                            $(this).off();
                        });

                        // Remove all event of answer pins
                        let answers = $(".answer");
                        answers.each(function() {
                            $(this).off();
                        });
                    }
                }
            }
        });

        // Modal button clicked
        $("#btnModal").on("click", function() {
            /* Print win or game over message */

            let modal = $("#modalDialog");
            // Show modal dialog
            modal.css({"display": "flex", "align-items": "center"});
            if (pinCounter == pinNumber) {
                // Print win message and user can submit the result
                modal.children().children(".modal-header").children().text("You Won!");
                modal.children().children(".modal-body").children().text("Congratulations! You cleared in " + $(".row-number").first().text() + " guesses.");
                modal.children().children(".modal-footer").html("\
                                                                <form action=\"/win\" method=\"post\">\
                                                                    <input name=\"duplicate\" type=\"hidden\" value=" + getDuplication() + ">\
                                                                    <input name=\"pins\" type=\"hidden\" value=" + getPinNumber() + ">\
                                                                    <input name=\"guess\" type=\"hidden\" value=" + $(".row-number").first().text() + ">\
                                                                    <button class=\"btn btn-primary\" type=\"submit\">Submit</button>\
                                                                </form>\
                                                                ");
            } else {
                // Print game over message
                modal.children().children(".modal-header").children().text("Game Over!");
                modal.children().children(".modal-body").children().text("Please try harder next time!");
                modal.children().children(".modal-footer").html("\
                                                                <button class=\"btn btn-secondary close\" type=\"button\">Close</button>\
                                                                ");
                $(".close").on("click", function() {
                    modal.fadeOut();
                });
            }
        });

        // New game button clicked
        $("#newGame").on("click", function() {
            let modal = $("#modalDialog");
            // Show modal dialog
            modal.css({"display": "flex", "align-items": "center"});
            modal.children().children(".modal-header").children().text("New Game?");
            modal.children().children(".modal-body").children().text("Are you sure you want to start a new game?");
            modal.children().children(".modal-footer").html("\
                                                            <button class=\"btn btn-secondary close\" type=\"button\">No</button>\
                                                            <a class=\"btn btn-primary\" href=\"/\" type=\"button\">Yes</a>\
                                                            ");
            $(".close").on("click", function() {
                modal.fadeOut();
            });

            $(window).off("beforeunload");
        });

        function checkColors() {
            /*
                Enable check button when user fill all the answer

                Disable check button if not all answer is filled
            */

            // Check each answer pin have color's class
            $(".pin-answer").children(".answer").each(function() {
                let pin = $(this).attr("class").split(/\s+/);

                for (var i = 0; i < answers.length; i++) {
                    if ($.inArray(pin[i], colors) > -1) {
                        counter++;
                        break;
                    }
                }
            });

            // Ensure answer pin filled is same as number of pin
            if (counter == pinNumber) {
                // Enable check button
                $("#btnCheck").removeAttr("disabled");
            } else {
                // Disable check button
                $("#btnCheck").attr("disabled", true);
                // Reset counter
                counter = 0;
            }
        }

        function checkCorrectColor(question, answer, correctPin) {
            /* Check user's answer for correct color pin */

            let correctColor = [];

            // Add the posiiton of pin to array without duplicating with the pin that has correct color and position
            for (var i = 0; i < question.length; i++) {
                if ($.inArray(i, correctPin) > -1) {
                    continue;
                } else if ($.inArray(answer[i], question) > -1) {
                    correctColor.push(i);
                }
            }

            return correctColor;
        }

        function checkCorrectPin(question, answer) {
            /* Check user's answer for correct color and position pin */

            let correctPin = [];

            // Add the postion of pin to array
            for (var i = 0; i < question.length; i++) {
                if (question[i] == answer[i]) {
                    correctPin.push(i);
                }
            }

            return correctPin;
        }

        function getAnswer() {
            /* Get submitted answer */

            var answer = [], color = [];

            // Ensure each answer pin have color's class
            $(".pin-answer").children(".answer").each(function() {
                let pin = $(this).attr("class").split(/\s+/);

                for (var i = 0; i < pin.length; i++) {
                    if ($.inArray(pin[i], colors) > -1) {
                        color.push(pin[i]);
                    }
                }

                if (color.length == 1) {
                    // Store color's class in array if only one color's class existed
                    answer.push(color[0]);
                } else if (color.length > 1) {
                    // Store last color's class in array if more than one color's class existed
                    answer.push(color[color.length - 1]);
                }

                // Reset array
                color = [];
            });

            return answer;
        }

        function getDuplication() {
            /* Get duplication that user selected in gamemode */

            if ($("#game").hasClass("duplicate")) {
                return true;
            } else {
                return false;
            }
        }

        function getPinNumber() {
            /* Get number of pins that user selected in gamemode */

            const pinNumber = ["4", "6", "8"];
            const pinNumberClass = ["pins-4", "pins-6", "pins-8"];
            let gameClass = $("#game").attr("class").split(/\s+/);

            for (var i = 0; i < gameClass.length; i++) {
                if ($.inArray(gameClass[i], pinNumberClass) > 0) {
                    let pinNum = gameClass[i].split("-");

                    for (var j = 0; j < pinNum.length; j++) {
                        if ($.inArray(pinNum[j], pinNumber) > 0) {
                            return parseInt(pinNum[j]);
                        }
                    }
                }
            }

            return 4;
        }

        function randomizeQuestion(pins, duplicate) {
            /* Randomize question based on gamemode */

            let question = [];
            while (question.length < pins) {
                var random = Math.floor(Math.random() * colors.length);

                if (duplicate) {
                    question.push(colors[random]);
                } else if ($.inArray(colors[random], question) == -1) {
                    question.push(colors[random]);
                }
            }

            return question;
        }

        function setChecked(checkPin, pinNumber) {
            /* Set checked class to the rest of small pin */

            while (checkCounter < pinNumber) {
                if (checkPin.eq(checkCounter).hasClass("check")) {
                    checkPin.eq(checkCounter).addClass("checked").removeClass("check");
                    checkCounter++;
                }
            }
        }

        function setCorrectColor(checkPin, correctColor) {
            /* Set small red pin to represent correct color pin */

            for (var i = 0; i < correctColor.length; i++) {
                if (checkPin.eq(checkCounter).hasClass("check")) {
                    checkPin.eq(checkCounter).addClass("checked correct-color").removeClass("check");
                    checkCounter++;
                }
            }
        }

        function setCorrectPin(checkPin, correctPin) {
            /* Set small green pin to represent correct color and position pin */

            for (var i = 0; i < correctPin.length; i++) {
                if (checkPin.eq(checkCounter).hasClass("check")) {
                    checkPin.eq(checkCounter).addClass("checked correct-pin").removeClass("check");
                    checkCounter++;
                }
            }
        }

        function setPin(pinNumber) {
            /* Set pins for question, answer and check based on number of pin user selected in gamemode */

            const pinAnswer = "<div class=\"circle answer\"></div>";
            const pinCheck = "<div class=\"check\"></div>";
            const pinQuestion = "<div class=\"circle question\">?</div>";
            let length = 0;

            while (length < pinNumber) {
                $(".pin-answer").append(pinAnswer);
                $(".pin-check").append(pinCheck);
                $(".pin-question").append(pinQuestion);
                length++;
            }

            switch(pinNumber) {
                case 4:
                    $(".pin-check").addClass("pin-check-4");
                    $(".rectangle-background").addClass("rectangle-background-4");
                    break;
                case 6:
                    $(".pin-check").addClass("pin-check-6");
                    $(".rectangle-background").addClass("rectangle-background-6");
                    break;
                case 8:
                    $(".pin-check").addClass("pin-check-8");
                    $(".rectangle-background").addClass("rectangle-background-8");
                    break;
            }
        }
    }

});