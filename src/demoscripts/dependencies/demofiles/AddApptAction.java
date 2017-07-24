import SQLException;
import Timestamp;
import ApptBean;
import DAOFactory;
import DBException;
import FormValidationException;
import ApptBeanValidator;

public class AddApptAction extends ApptAction {
	private ApptBeanValidator validator = new ApptBeanValidator();
	
	public AddApptAction(DAOFactory factory, long loggedInMID) {
		super(factory, loggedInMID);
	}
	
	public String addAppt(ApptBean appt, boolean ignoreConflicts) throws FormValidationException, SQLException, DBException {
		validator.validate(appt);
		if(appt.getDate().before(new Timestamp(System.currentTimeMillis()))) {
			return "The scheduled date of this Appointment ("+appt.getDate()+") has already passed.";
		}
		
		if(!ignoreConflicts){
			if(getConflictsForAppt(appt.getHcp(), appt).size()>0){
				return "Warning! This appointment conflicts with other appointments";
			}
		}
		
		try {
			apptDAO.scheduleAppt(appt);
			return "Success: " + appt.getApptType() + " for " + appt.getDate() + " added";
		}
		catch (SQLException e) {
			
			return e.getMessage();
		} 
	}	
	
	

}
