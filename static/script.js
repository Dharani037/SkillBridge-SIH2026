document.addEventListener("DOMContentLoaded", function () {

    console.log("SkillBridge frontend loaded successfully.");

    const resumeInput = document.getElementById("resumeInput");

    if (resumeInput) {

        resumeInput.addEventListener("change", function () {

            if (this.files.length > 0) {

                const file = this.files[0];

                // PDF validation
                if (!file.name.toLowerCase().endsWith(".pdf")) {
                    alert("Please select a PDF resume.");
                    this.value = "";
                    return;
                }

                // 5 MB validation
                if (file.size > 5 * 1024 * 1024) {
                    alert("Resume size must be less than 5 MB.");
                    this.value = "";
                    return;
                }
            }
        });
    }

});